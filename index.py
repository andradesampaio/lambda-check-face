import boto3 as boto3

s3 = boto3.resource('s3')
client = boto3.client('rekognition')
#client.create_collection(CollectionId='draande-faces')
#client.delete_collection(CollectionId='draande-faces')


def list_images():
    images = []
    bucket = s3.Bucket('draande-images')
    for imagem in bucket.objects.all():
        images.append(imagem.key)
    return images


def index_colections(images):
    for image in images:
        response = client.index_faces(
            CollectionId='draande-faces',
            Image={
                'S3Object': {
                    'Bucket': 'draande-images',
                    'Name': image
                }
            },
            ExternalImageId=image[:-4],
            DetectionAttributes=[]
        )
    print(response)
    return response


images = list_images()
index_colections(images)
