FROM python:3.7

RUN apt-get update \
 && apt-get install -y locales \
 && dpkg-reconfigure -f noninteractive locales \
 && locale-gen C.UTF-8 \
 && /usr/sbin/update-locale LANG=C.UTF-8 \
 && echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen \
 && locale-gen \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN apt-get update \
 && apt-get install -y curl unzip \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

ENV PYTHONHASHSEED 0
ENV PYTHONIOENCODING UTF-8
ENV PIP_DISABLE_PIP_VERSION_CHECK 1

# JAVA
RUN echo 'deb "http://ftp.debian.org/debian" stretch main\ndeb-src "http://ftp.de.debian.org/debian" stretch main' > /etc/apt/sources.list.d/java.list
RUN apt-get update && apt-get install -y openjdk-8-jdk && rm -rf /var/lib/apt/lists/*

# HADOOP
ENV HADOOP_VERSION 2.7.3
ENV HADOOP_HOME /usr/hadoop-$HADOOP_VERSION
ENV HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
ENV PATH $PATH:$HADOOP_HOME/bin
RUN curl -sL --retry 3 \
  "http://archive.apache.org/dist/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz" \
  | gunzip \
  | tar -x -C /usr/ \
 && rm -rf $HADOOP_HOME/share/doc \
 && chown -R root:root $HADOOP_HOME\
 && chmod 755 $HADOOP_HOME

# SPARK
ENV PYSPARK_SUBMIT_ARGS="--packages org.mongodb.spark:mongo-spark-connector_2.11:2.2.0 pyspark-shell"

ENV SPARK_VERSION 2.3.1
ENV SPARK_PACKAGE spark-${SPARK_VERSION}-bin-without-hadoop
ENV SPARK_HOME /usr/spark-${SPARK_VERSION}
ENV SPARK_DIST_CLASSPATH="$HADOOP_HOME/etc/hadoop/*:$HADOOP_HOME/share/hadoop/common/lib/*:$HADOOP_HOME/share/hadoop/common/*:$HADOOP_HOME/share/hadoop/hdfs/*:$HADOOP_HOME/share/hadoop/hdfs/lib/*:$HADOOP_HOME/share/hadoop/hdfs/*:$HADOOP_HOME/share/hadoop/yarn/lib/*:$HADOOP_HOME/share/hadoop/yarn/*:$HADOOP_HOME/share/hadoop/mapreduce/lib/*:$HADOOP_HOME/share/hadoop/mapreduce/*:$HADOOP_HOME/share/hadoop/tools/lib/*"
ENV PATH $PATH:${SPARK_HOME}/bin
RUN curl -sL --retry 3 \
  "https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/${SPARK_PACKAGE}.tgz" \
  | gunzip \
  | tar x -C /usr/ \
 && mv /usr/$SPARK_PACKAGE $SPARK_HOME \
 && chown -R root:root $SPARK_HOME\
 && chmod 755 $SPARK_HOME

# WEB
COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt  && rm requirements.txt 

ENV WEB_HOME /usr/src/app
ENV WEB_SPARK_MODELS_PATH ${WEB_HOME}/server/main/spark_models

RUN mkdir -p $WEB_HOME

ENV APP_SETTINGS server.config.DevelopmentConfig

# add app
COPY ./services/web/project $WEB_HOME

RUN chown -R root:root $WEB_HOME
RUN chmod 755 $WEB_HOME

USER root
