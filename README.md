This a cloud-based, real-time streaming data pipeline for a simulated fintech trading firm "YuppieStreet Trading Co." which has a system that ingests live price tick events from 22 simulated instruments on JSE and ZAR-denominated cryptocurrency pairs. The system/pipeline/stream processes them through Azure Stream Analytics, with results in Azure CosmosDB, then visualises KPIs on a 3 page Power BI dashboard, the system also dispatches automated anomaly alserts via Azure Logic Apps.

Prices are generated using the Black-Scholes Geometric Brownian Motion formula. 
price(t+1) = price(t) x e^(u*dt + s*sqrt(dt) * Z)

where:
  u  = drift term (0.05 annualised — slight upward market bias)
  s  = volatility (per-instrument, from config — e.g. 0.018 for JSE:SOL)
  dt = 1 / 98,280  (one tick as fraction of a trading year)
  Z  = random shock drawn from standard normal distribution N(0,1)
  e  = Euler's number (implemented via numpy.exp)

The stream has 5 -like streaming behaviours are  injected by the simulator to demonstrate that the pipeline handles real-world event stream challenges: 
-Variable throughput	Random sleep 0.1s–2.0s between event sends	Always active
-Burst traffic	20 events sent rapidly approximately every 60 seconds	Every ~60s
-Out-of-order events	event_ts backdated by 30 seconds on injection	5% of events
-Duplicate events	Previous event resent with identical event_id	3% of events
-Late arrivals	35 second delay before send; is_late=True flag set	4% of events

FEATURES: 
*Real time analytics
*ML Anomaly Detection Method: AnomalyDetection_SpikeAndDip Confidence Interval: 95% and Detection Window: 120 seconds
*End-to-end trading data pipeline simulation
*Cosmos DB integration
*Power BI dashboard built on top of the simulated pipeline output.

TO RUN/USE
1. create a virtual environment
2. install the requirements
3. set up your keys on azure
4. Run the whole file in the cmb/terminal with python -m simulator.main
5. the stream will begin, if you Stream analytics Job on Azure is on, eventhubs and cosmos db are all set up it will stream data to it.
6. view your power bi/ create visuals
