# syntax=docker/dockerfile:1
FROM python:3.8

ENV PATH=$PATH:/home/user/.local/bin \
   PYTHONFAULTHANDLER=1 \
   PYTHONUNBUFFERED=1 \
   PIP_DISABLE_PIP_VERSION_CHECK=on \
   PIPENV_COLORBLIND=true \
   PIPENV_NOSPIN=true \
   PIP_NO_CACHE_DIR=off \
   PIP_USER=1


WORKDIR /srv

# Essential tools and xvfb
RUN apt-get update && apt-get install -y \
    software-properties-common \
    unzip \
    xvfb \
    jq

# install google chrome
RUN wget -q --output-document - https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json|jq ".channels.Stable.version"|sed 's/"//g'>chrome_version
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable
RUN chmod 777 /usr/bin/google-chrome

# install chromedriver
RUN apt-get install -yqq unzip

RUN wget -O /tmp/chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/$(cat chrome_version)/linux64/chromedriver-linux64.zip

RUN unzip /tmp/chromedriver.zip -d /usr/local/bin/
RUN chmod 777 /usr/local/bin/chromedriver-linux64/chromedriver
RUN mv /usr/local/bin/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver

# set display port to avoid crash
ENV DISPLAY=:99
# Run as a non-root user.
RUN useradd -ms /bin/bash -u 1000 user \
&& chown -R user:user /srv
USER user

# Create a dummy service directory for the dependency installation.
RUN mkdir -p /srv/adap
COPY --chown=user:user requirements.txt /srv/
RUN pip3 install -r requirements.txt

RUN --mount=type=secret,id=GITHUB_KEY,uid=1000 <<EOT
    export GITHUB_TOKEN=$(cat /run/secrets/GITHUB_KEY) &&
    pip3 install --no-cache-dir git+https://${GITHUB_TOKEN}@github.com/Appen-International/appen-project-flow-sdk.git
EOT


RUN mkdir -p /srv/allure_result_folder
RUN mkdir -p /srv/result
RUN mkdir -p /srv/adap/Failed_scenarios
RUN mkdir -p /srv/report_result
ENV PYTHONPATH "${PYTHONPATH}:/srv"

# overwrite ssl module
COPY --chown=user:user ./scripts/ssl.py /usr/local/lib/python3.8/ssl.py
COPY --chown=user:user . .

# Set the command executed first when the container run
ENTRYPOINT ["bash"]