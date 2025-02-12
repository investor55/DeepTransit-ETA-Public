FROM public.ecr.aws/lambda/python:3.9

ENV AWS_DEFAULT_REGION=us-east-1

# Copy requirements first to leverage Docker cache
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt

# Copy your application code
COPY fetch_translink_api.py ${LAMBDA_TASK_ROOT}

# Command to run your Lambda function
CMD [ "fetch_translink_api.lambda_handler" ]