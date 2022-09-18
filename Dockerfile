FROM python

WORKDIR /app
COPY . .
RUN make install
VOLUME "data"

CMD [ "bash" ]
