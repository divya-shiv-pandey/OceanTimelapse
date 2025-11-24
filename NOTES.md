# Overall Approach & Tech Choices

### Architecture Decison
I chose a simple Flask-based web application with Leaflet for mapping. This is a lightweight stack that gets the job done without over-engineering.

**Backend:**
- **Flask**: Simple,flexible web framework. Overkill for just serving a map but needed for the API endpoint to query wave data dynamicly
- **xarray**: Perfect library for NetCDF files- makes working with multi-dimensional data straightforward and has built-in nearest-neighbor selection
- **NumPy**: For fast numerical operations (max, min, mean calculations)

**Frontend:**
- **Leaflet.js**: Lightweight mapping library. Considered Folium (Python wrapper) but wanted more control over the UI/UX
- **Vanilla JS**: No frameworks needed for this simple interactive map
- **OpenStreetMap**: Free tile provider, works well for global coverage

### Data Handling Strategey
The dataset is loaded once when Flask starts rather than on each request. The file is only ~50MB so keeping it in memory is fine and makes responses instant. For production with 70 years of data this wouldnt work.

### Why This Stack
- Fast to implement
- Easy to understand and maintain
- No build step or complex tooling
- Works on any machine with Python installed
- Leaflet handles all the map complexity (projections, zoom, panning)

## Q1 Answer: Maximum Wave Height at (0.0, 0.0)

**Answer: 2.326 meters**

The data has 24 hourly readings for 2019-01-01.Wave height increased throughout the day from 2.081m at midnight to 2.326m at 23:00.

## Q2: Interactive Map

Created a Flask app with Leaflet map.User clicks anywhere and gets the max wave height for that day. The backend finds the nearest grid point and returns the maximum hmax value across all 24 hours.

Key features:
- Click anywhere on the map
- Shows max/mean/min wave height for the location
- Displays actual grid coordinates used (since we snap to nearest point)
- Simple error handling for out-of-bounds clicks
- Clean UI focused on the data

## Q3: Scaling to 70+ Years of Data
### Approach for Historical Maximum Waves

1. Working Backward from the Constraints  
The main headache is data size. One day is ~50MB, so 70 years of hourly global data quickly explodes to ~2–3TB if uncompressed. Anything that tries to load raw NetCDF directly at request time is dead on arrival — too slow, too heavy, and doesn’t scale.

So I started from that constraint and worked backwards: how do I make this queryable in tiny pieces instead of giant slabs of data?

That led to three ideas:
- chunk the data
- move heavy processing offline
- use storage formats that are built for slicing over HTTP

NetCDF is great for scientific workflows, but not ideal for web apps. Zarr is basically built for this exact use case: chunked, cloud-native, HTTP-friendly access. So that became the base.

2. Selecting Zarr + Xarray  
Zarr gives me:
- real lazy loading
- storage in S3 (or any object store)
- fast slicing along the time dimension
- tight integration with xarray

Given the goal (fast time-based queries, small payloads), this combo fits really well. Xarray does the heavy lifting: reading data, chunking it, and computing daily maxima without a bunch of custom logic.

3. Precomputing Daily Max and Hourly Chunks  
The logic here is simple:
- users usually ask about specific dates -> precompute daily max
- users might want animations → keep hourly chunks around

That means most of the heavy work (90%+) moves into an offline preprocessing step. We trade storage for speed, which is totally fine for this problem.

4. Keeping Chunk Size Small  
Chunking choice:
- time: 1
- latitude: 261
- longitude: 720

This makes “one hour = one chunk”.

Why this matters:
- we don’t have to load a whole day at once
- plays nicely with CDN caching
- keeps memory use low

Basically it’s tuned for user-facing latency, not for batch processing convenience.

5. Rendering Strategy (WebGL or Map Tiles)  
For rendering, I lean on the browser and GPU instead of the backend.

The backend just returns raw grids. The frontend handles:
- color scaling
- animation
- map projection

Using WebGL or map tiles means the server stays lean, and the browser does the visually heavy stuff. The server doesn’t have to know anything about how the map looks — it just serves data.

Lazy loading: Use xarray with dstd to work with datasets larger than memory. Only load chunks as needed.

Caching layer: Add Redis to cache recently queried locations since users often click nearby points.

## Q4: Questions for the Desinger

If the designer wants users to load the full 70-year dataset and animate any date range, I’d push back with a few questions before jumping into a solution.


**1. Whats the actual user need here?**
   - Do users actually need to scrub through 70 years of dates, or are they just looking for specific storms?
   - If its just about big events, we should just pre-calculate those specific periods.
   - Would save us a ton of optimization work if we just focus on the popular stuff.

**2. Temporal resolution - how granular do we need to be?**
   - Hourly animation for 70 years is like 600k frames. Thats insane.
   - Can we get away with daily maxes or weekly averages? That cuts the data down massive amounts.
   - Also, who is gonna watch 70 years of hourly data? That would take forever.

**3. Scale - how many people are using this?**
   - If we have to load the full dataset for every user, bandwidth costs are gonna kill us.
   - 10 users is fine, 10k users changes the whole architecture.
   - Maybe we should just render video on the server instead of sending raw data to the browser?

**4. Load times - whats acceptable?**
   - Nobody is gonna wait 5 mins for a map to load.
   - Whats the max wait time? 5 secs? 30?
   - This basically dictates how much pre-processing we have to do.

**5. Is this actually critical?**
   - If this is a core feature, we need a real budget for CDNs and processing pipelines.
   - If its just a "nice to have", lets strip it back to a simpler MVP.
   - Honestly, pre-rendered videos of cool storms might be way cheaper and better for the user anyway.


## Trade-offs Made for Time Constraints

### What I Simplified
- No zarr format approach used due to contraints.
- Couldnt implement the suggest approoach: lack of data and time to ijmplement the whole thing.
- No authentication: Real app would need user accounts, especially if query costs money
- No rate limiting. Could be abused easily.
- No input validation on frontend: Just basic backend checks
- Error handling is basic. Production would need better logging, monitoring.
- Single-threaded Flask: Would use Gunicorn with multiple workers in production
- No caching: Every request queries the dataset fresh
- No loading state improvements: Could add progress bars,lazy loading, skeleton screens
- Hardcoded file paths. Should be config-driven.
- No deployment setup: Would need Docker proper, WSGI server , reverse proxy

### Production Improvments
1. **Approach:**
   - Implement the full 70-year historical data approach.
   - Prioritize memory management and move heavy computations offline rather than doing them on-the-fly.
   - Have a more vivid and cloud based architecture.

2. **Infrastucture:**
   - Dockerize the entire stack for easy deployment across enviroments.
   - Use environment variables for configuration (separating dev/prod) instead of hardcoding file paths.

3. **Data Layer:**
   - Switch to the Zarr format mentioned in Q3 to handle chunking better amd faster laoding.
   - Potentially add PostGIS if the spatial queries get more complex.
   - Redis caching is esential,users often click the same geographic spots.
   - Use Dask for lazy loading to keep RAM usage under control.

4. **API Improvements:**
   - Return semantic HTTP error codes, not just generic server errors.
   - Implement rate limiting to protect the server from traffic spikes.
   - Fix CORS settings to support hosting the frontend on a different domain.

5. **Frontend:**
   - Needs loading spinners/animations - right now it just hangs while fetching.
   - Better error messages when clicks go out of bounds.
   - Make it work better on mobile.
   - Add keyboard nav/accesibility stuff.

6. **Monitoring & Testing:**
   - Add real logging (structured logs), something like cloudwatch etc.
   - Track response times to see where its slow.
   - Need unit tests for the math parts and integration tests for the API.
   - Load testing to see when it breaks.

## AI Usage

I used AI assistance for parts of this project:
- HTML/CSS boilerplate to speed up frontend work
- Helping with writing smaller parts where i struggeled with syntax for new libs.
- Linting, commenting and aligining code and finding weaker parts of the code
- Rewriting my answers in a structured and presentable manner for readme.md and notes.md

However, core logic for data processing, architecture decisions, and problem-solving approach were done independently. The code structure and implementation strategy came from my experience building similar geospatial applications.

All written explanations and technical decisions in this document are my own analysis.(Although this document was made using AI by rewriting and structuring the rough sketch of the answers.)

## Running the Application

1. Install dependencies:
```bash
pip install xarray netCDF4 numpy flask
```

2. Run the app:
```bash
python app.py
```

3. Open browser to `http://localhost:5000`

4. Click anywhere on the map to see wave height data