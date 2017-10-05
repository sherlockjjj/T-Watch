# Real Time Twitter Stream Analysis via Kafka and Spark Streaming

### Motivation:
Build a data product that could process streaming data and has an end-to-end data pipeline that could be easily scaled upon request.

### Model Training:
1. Training tfidf and random forest model using pipeline on spark ML
2. Saving models to S3

### Real Time Analysis:
1. Collecting real time twitter streams through Kafka
2. Integrating Kafka with spark streaming
3. Loading saved model to predict incoming streams in spark streaming
4. Storing incoming streams to MongoDB in spark streaming
5. Fetching data from MongoDB and publishing results on web application via flask

### Data Flow
![Real Time Data Flow](https://github.com/sherlockjjj/capstone/blob/master/images/data_flow.png)

## Tools:
### AWS EC2 EMR S3, SES
### Kafka
### Spark (spark streaming, spark sql, spark ml)
### Flask
### MongoDB
### Plotly
### Twilio 
