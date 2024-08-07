# Define global args
# ARG FUNCTION_DIR="/tmp/"
# ARG FUNCTION_DIR=${LAMBDA_TASK_ROOT}
ARG FUNCTION_DIR="/home/app/"
ARG RUNTIME_VERSION="3.8"
ARG DISTRO_VERSION="3.12"
ARG CHECK_DIR='/home/app/checkpoint/'
ARG MODELS_DIR='/home/app/models/'
ARG MODELS_DIR_UTIL='/home/app/models/utils/'
ARG TMP_DIR="/home/app/tmp/"
# Stage 1 - bundle base image + runtime
# Grab a fresh copy of the image and install GCC
FROM python:${RUNTIME_VERSION} AS python-alpine
# Install GCC (Alpine uses musl but we compile and link dependencies with GCC)
#RUN apk add --no-cache \
#    libstdc++

RUN apt-get update \
    && apt-get install -y cmake ca-certificates libgl1-mesa-glx
RUN python${RUNTIME_VERSION} -m pip install --upgrade pip

# Stage 2 - build function and dependencies
FROM python-alpine AS build-image
# Install aws-lambda-cpp build dependencies
#RUN apk add --no-cache \
#    build-base \
#    libtool \
#    autoconf \
#    automake \
#    libexecinfo-dev \
#    make \
#    cmake \
#    libcurl
# Include global args in this stage of the build
ARG FUNCTION_DIR
ARG RUNTIME_VERSION
ARG CHECK_DIR
ARG MODELS_DIR_UTIL
ARG TMP_DIR
# Create function directory
# RUN mkdir -p ${FUNCTION_DIR}
RUN mkdir -p ${CHECK_DIR}
RUN mkdir -p ${MODELS_DIR_UTIL}
ARG mkdir -p ${TMP_DIR}

# Optional – Install the function's dependencies
# RUN python${RUNTIME_VERSION} -m pip install -r requirements.txt --target ${FUNCTION_DIR}
# Install Lambda Runtime Interface Client for Python
RUN python${RUNTIME_VERSION} -m pip install awslambdaric --target ${FUNCTION_DIR}

# Stage 3 - final runtime image
# Grab a fresh copy of the Python image
FROM python-alpine
# Include global arg in this stage of the build
ARG FUNCTION_DIR
# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}
# Copy in the built dependencies
COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}
# (Optional) Add Lambda Runtime Interface Emulator and use a script in the ENTRYPOINT for simpler local runs
ADD https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /usr/bin/aws-lambda-rie
RUN chmod 755 /usr/bin/aws-lambda-rie

# Install ffmpeg
# RUN apt-get install -y ffmpeg

# Copy handler function
COPY requirements.txt ${FUNCTION_DIR}
RUN python${RUNTIME_VERSION} -m pip install -r requirements.txt --target ${FUNCTION_DIR}
COPY entry.sh /

# Copy function code
COPY handler.py ${FUNCTION_DIR}
RUN chmod 777 /entry.sh

# Copy face-recognition files to /home/app/
COPY eval_face_recognition.py ${FUNCTION_DIR}
RUN chmod 777 eval_face_recognition.py
COPY build_custom_model.py ${FUNCTION_DIR}
RUN chmod 777 build_custom_model.py

# Copy to /home/app/checkpoint/
ARG CHECK_DIR
WORKDIR ${CHECK_DIR}
COPY labels.json ${CHECK_DIR}
RUN chmod 777 /home/app/checkpoint/labels.json
COPY model_vggface2_best.pth ${CHECK_DIR}
RUN chmod 777 /home/app/checkpoint/model_vggface2_best.pth

# Copy to /home/app/models/
ARG MODELS_DIR
WORKDIR ${MODELS_DIR}
COPY inception_resnet_v1.py ${MODELS_DIR}
RUN chmod 777 /home/app/models/inception_resnet_v1.py
COPY modelfeatures.pt ${MODELS_DIR}
RUN chmod 777 /home/app/models/modelfeatures.pt

# Copy to /home/app/models/util/
ARG MODELS_DIR_UTIL
WORKDIR ${MODELS_DIR_UTIL}
COPY download.py ${MODELS_DIR_UTIL}
RUN chmod 777 /home/app/models/utils/download.py

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
# CMD [ "handler.handler" ]
ARG FUNCTION_DIR
# RUN chmod 777 -R 
WORKDIR ${FUNCTION_DIR}
RUN chmod 777 -R /home/app/
ENTRYPOINT [ "/entry.sh" ]
CMD [ "handler.face_recognition_handler" ]
