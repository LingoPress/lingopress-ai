FROM public.ecr.aws/lambda/python:3.12-x86_64

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt ${LAMBDA_TASK_ROOT}/

RUN pip install -r requirements.txt

ADD ./model_all-MiniLM-L6-v2 ${LAMBDA_TASK_ROOT}/model_all-MiniLM-L6-v2/

COPY ./*.py ${LAMBDA_TASK_ROOT}/


CMD ["main.handler"]