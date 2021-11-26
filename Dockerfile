FROM programmingerror/ultroid:b0.1

ENV TZ=Asia/Kolkata
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# clone the repo and change workdir
RUN git clone --branch qovery https://github.com/yashoswalyo/Auto-Filter-Bot/ /root/filter/
WORKDIR /root/filter/

COPY requirements.txt /deploy/

RUN pip3 install --no-cache-dir -r /deploy/requirements.txt
CMD ["python", "main.py"]