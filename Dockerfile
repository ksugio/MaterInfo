FROM python:3.11

# install libralies
RUN apt update
RUN apt upgrade -y
RUN apt install vim -y
RUN apt install libgl1-mesa-dev -y

RUN pip install --upgrade pip
RUN pip install wheel
RUN pip install Django==4.2
RUN pip install MPLn23d
RUN pip install MPImfp
RUN pip install django-bootstrap5
RUN pip install opencv-python
RUN pip install pillow
RUN pip install pandas
RUN pip install matplotlib
RUN pip install seaborn
RUN pip install scikit-learn
RUN pip install djangorestframework
RUN pip install markdown
RUN pip install django-filter
RUN pip install djangorestframework-simplejwt
RUN pip install djoser
RUN pip install ldap3
RUN pip install django-mdeditor
RUN pip install diff-match-patch
RUN pip install django_cleanup
RUN pip install pybeads
RUN pip install lmfit
RUN pip install GitPython
RUN pip install xgboost
RUN pip install lightgbm
RUN pip install optuna
RUN pip install umap-learn
RUN pip install skl2onnx
RUN pip install onnxmltools
RUN pip install onnxruntime
RUN pip install shap

RUN pip install mysqlclient
RUN pip install uwsgi

# copy files
RUN mkdir /MaterInfo
WORKDIR /MaterInfo
COPY ./ /MaterInfo

# run server
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
CMD ["uwsgi", "--ini", "uwsgi.ini"]
