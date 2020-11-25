# Build and install guide

## build deb package using docker
```
docker build -t sytr:latest .
docker run --name sytrdeb sytr:latest
docker cp sytrdeb:/sytr_1.0.0_amd64.deb .

```

## install 
```
sudo apt install ./sytr_1.0.0_amd64.deb
```

## Configure 
- [create or select google cloud project and Enable the Cloud Translation API](https://cloud.google.com/translate/docs/setup#python)
- copy Google Translate Api json key in the location /etc/sytr/
- create /etc/sytr/.env containing the necessary env variables :
```
GOOGLE_APPLICATION_CREDENTIALS="/etc/sytr/sytr-c97b58619c27.json"
GOOGLE_PROJECT_ID=plasma-system-296217
QUERIES_PER_SEC=10
```

## start the Google translate daemon
```
sudo systemctl enable sytr.service
sudo systemctl start sytr.service
```

## Try gtranslate CLI
```
cat > input << EOF
Buna dimineata
Buona sera
Gutten tag
Arrivederci
EOF

gtranslate -f input -l en
``` 

## List of error codes
```
    ERR_GTM_0001: QUERIES_PER_SEC is invalid, it should be a integer number higher than 0
    ERR_GTM_0002: GOOGLE_PROJECT_ID env variable is missing
    ERR_GTM_0003: GOOGLE_APPLICATION_CREDENTIALS env variable is missing
    ERR_GTM_0004: file specified in GOOGLE_APPLICATION_CREDENTIALS does not exist / is not readable
    ERR_GTM_0005: Google Key is invalid
    ERR_GTM_0006: Google authentication failed
```


# Others

## errors encountered while using google cloud api in a multi threaded context:
[Stack overflow question ssl error using multiprocessing](https://stackoverflow.com/questions/58241849/ssl-error-using-multiprocessing-in-python-with-google-cloud-services) 


# create python wheel 
```
pip install -r requirements.txt
pytest -v
python setup.py sdist bdist_wheel
```
