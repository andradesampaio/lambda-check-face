import boto3
import json

client = boto3.client('rekognition')
s3 = boto3.resource('s3')


def detect_faces():
    faces_detected = client.index_faces(
        CollectionId='draande-faces',
        DetectionAttributes=['DEFAULT'],
        ExternalImageId='IMAGE_TEMP',
        Image={
            'S3Object': {
                'Bucket': 'draande-images',
                'Name': '_analise.png'
            }
        }
    )
    return faces_detected


def create_list_face_id_detected(face_detected):
    face_id_detected = []
    for images in range(len(face_detected['FaceRecords'])):
        face_id_detected.append(face_detected['FaceRecords'][images]['Face']['FaceId'])
    return face_id_detected


def compare_images(face_id_detected):
    result_compare = []
    for face_id in face_id_detected:
        result_compare.append(
            client.search_faces(
                CollectionId='draande-faces',
                FaceId=face_id,
                MaxFaces=10,
                FaceMatchThreshold=98
            )
        )
    return result_compare


def generate_data_json(result_compare):
    data_json = []
    for face_matches in result_compare:
        if (len(face_matches.get('FaceMatches'))) >= 1:
            profile = dict(name=face_matches['FaceMatches'][0]['Face']['ExternalImageId'],
                           faceMatch=round(face_matches['FaceMatches'][0]['Similarity'], 2))
            data_json.append(profile)
    return data_json


def publish_dada(data_json):
    file = s3.Object('draande-web', 'data.json')
    file.put(Body=json.dumps(data_json))


def delete_image_colection(face_id_detected):
    client.delete_faces(
        CollectionId='draande-faces',
        FaceIds=face_id_detected,
    )


def main(event, context):
    face_detected = detect_faces()
    face_id_detected = create_list_face_id_detected(face_detected)
    result_compare = compare_images(face_id_detected)
    data_json = generate_data_json(result_compare)
    publish_dada(data_json)
    delete_image_colection(face_id_detected)
    print(json.dumps(data_json, indent=4))
