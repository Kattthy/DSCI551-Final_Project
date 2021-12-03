from django.shortcuts import render, redirect
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger
from .models import Genre, Style, Artist, Picture, Features, Prediction, Predict_option
import os
import joblib as jl
from boto3.session import Session
import io
import photos.model as model

# Create your views here.
def album(request):
    style = request.GET.get('style')
    searchword = request.GET.get('SearchWord')
    if style == None:
        pictures = Picture.objects.all()[:12]
    else:
        pictures = Picture.objects.filter(style__name = style)[:12]
    if searchword != None:
        pictures = Picture.objects.filter(name__icontains = searchword)[:12]
    styles = Style.objects.all()
    context = {'styles': styles, 'pictures': pictures}
    return render(request, 'photos/album2.html', context)



def album2(request):
    style = request.GET.get('style')
    style = None
    if style == None:
        #pictures = Picture.objects.all()[:20]
        pictures_all = Picture.objects.all()
        paginator = Paginator(pictures_all, 9)
        page = request.GET.get('page')
        try:
            # 通过获取上面的page参数，查询此page是否为整数并且是否可用
            subject_obj = paginator.page(page)
        except PageNotAnInteger:
            subject_obj = paginator.page(1)
        except (EmptyPage, InvalidPage):
            subject_obj = paginator.page(paginator.num_pages)
    else:
        #pictures = Picture.objects.filter(style__name=style)[:20]
        pictures_all = Picture.objects.filter(style__name=style)
        paginator = Paginator(pictures_all, 9)
        page = request.GET.get('page')
        try:
            # 通过获取上面的page参数，查询此page是否为整数并且是否可用
            subject_obj = paginator.page(page)
        except PageNotAnInteger:
            subject_obj = paginator.page(1)
        except (EmptyPage, InvalidPage):
            subject_obj = paginator.page(paginator.num_pages)

    styles = Style.objects.all()
    context = {'styles':styles, 'subject_obj':subject_obj}
    return render(request,'photos/album.html', context)

def viewPicture(request, pk):
    picture = Picture.objects.get(name=pk)
    features = Features.objects.filter(image_id=pk)[:1]
    return render(request, 'photos/picture.html', {'picture': picture, 'features':features})

def extract(request, pk):
    picture = Picture.objects.get(name=pk)
    print('pk:',pk)
    cmd = "/Users/kw/PycharmProjects/FinalProject2/museum/spark-3.1.2-bin-hadoop3.2/bin/spark-submit /Users/kw/Desktop/Study/2021Fall/DSCI551/Final_Project/project/Codes/spark_feature_extraction_1128/extract_feature.py "+str(pk)
    print(cmd)
    os.system(cmd)
    features = Features.objects.filter(image_id=pk)[:1]
    return render(request, 'photos/picture.html', {'picture': picture, 'features':features})

rds_info = {
        'host': "wikiartdb.cv8worynfzsx.us-west-1.rds.amazonaws.com",
        'user': "admin",
        'password': "wikiartdb",
        'db': "wikiart",
        'port': 3306
    }
predict_model = model.PredictModel(rds_info=rds_info)

def predict(request):
    AWSAccessKeyId = "AKIA3UZI2QOSQSCCDTM4"
    AWSSecretKey = "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"
    session = Session(aws_access_key_id=AWSAccessKeyId, aws_secret_access_key=AWSSecretKey,
                           region_name='us-east-2')
    s3 = session.resource('s3')
    client = session.client('s3')
    predict_options = Predict_option.objects.all()
    predict_history = Prediction.objects.order_by('-id')[:10]
    if request.method == 'POST':
        data = request.POST
        images = request.FILES.getlist('images')
        if data['predict'] != 'none':
            predict_option = Predict_option.objects.get(id = data['predict'])
            #print('predict_option:',predict_option.name)
            predict_result = 'a'
            for image in images:
                url_path = client.generate_presigned_url('get_object', Params={'Bucket': 'acrawdata', 'Key': image.name},ExpiresIn=3600)
                prediction = Prediction.objects.create(
                    image=image,
                    predict_option = predict_option,
                    #predict_result = predict_result,
                    url_path = url_path,
                )
                name = image.name
                print(name)
                extract_cmd = '/Users/kw/PycharmProjects/FinalProject2/museum/spark-3.1.2-bin-hadoop3.2/bin/spark-submit /Users/kw/Desktop/Study/2021Fall/DSCI551/Final_Project/project/Codes/spark_feature_extraction_predict/extract_feature.py ' + name
                print(extract_cmd)
                os.system(extract_cmd)
                pred_result = predict_model.predict(predict_option.name, name)
                if predict_option.name == 'style':
                    predict_result = Style.objects.get(id=pred_result).name
                elif predict_option.name == 'genre':
                    predict_result = Genre.objects.get(id=pred_result).name
                elif predict_option.name == 'artist':
                    predict_result = Artist.objects.get(id=pred_result).name
                prediction.predict_result = predict_result
                prediction.save()
                print('pred_result:',predict_result)
    context = {'predict_options': predict_options, 'predict_history':predict_history}
    return render(request,'photos/predict.html', context)


def upload(request):
    AWSAccessKeyId = "AKIA3UZI2QOSQSCCDTM4"
    AWSSecretKey = "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"
    session = Session(aws_access_key_id=AWSAccessKeyId, aws_secret_access_key=AWSSecretKey,
                      region_name='us-east-2')
    s3 = session.resource('s3')
    client = session.client('s3')
    styles = Style.objects.all()
    artists = Artist.objects.all()
    genres = Genre.objects.all()
    if request.method == 'POST':
        data = request.POST
        images = request.FILES.getlist('images')

        if data['style'] != 'none':
            style = Style.objects.get(id=data['style'])
        elif data['style_new'] != '':
            style, created = Style.objects.get_or_create(
                name=data['category_new'])
        else:
            style = None

        if data['artist'] != 'none':
            artist = Artist.objects.get(id=data['artist'])
        elif data['artist_new'] != '':
            artist, created = Artist.objects.get_or_create(
                name=data['artist_new'])
        else:
            artist = None

        if data['genre'] != 'none':
            genre = Genre.objects.get(id=data['genre'])
        elif data['genre_new'] != '':
            genre, created = Style.objects.get_or_create(
                name=data['genre_new'])
        else:
            genre = None

        for image in images:
            url_path = client.generate_presigned_url('get_object', Params={'Bucket': 'acrawdata', 'Key': image.name}, ExpiresIn=3600)
            picture =Picture.objects.create(
                name = data['name'],
                artist = artist,
                genre = genre,
                style = style,
                image=image,
                url_path = url_path,
            )

        return redirect(viewPicture, pk=data['name'])

    context = {'styles': styles, 'genres':genres, 'artists':artists}
    return render(request,'photos/upload.html',context)

