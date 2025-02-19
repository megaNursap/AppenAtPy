import uuid

frame_annotation = [
    {
        'annotated_by': "human",
        'category': "Left Hand",
        'height': 0,
        'id': "left_hand_box",
        'type': "box",
        'visibility': "hidden",
        'width': 0,
        'x': 0,
        'y': 0
    },
    {
        'annotated_by': "human",
        'category': "Right Hand",
        'height': 69.71005249023438,
        'id': "right_hand_box",
        'type': "box",
        'visibility': "visible",
        'width': 67.00828552246094,
        'x': 281.22459411621094,
        'y': 530.8907775878906
    },
    {
        'annotated_by': "human",
        'category': "Left Hand",
        'height': 51,
        'id': "c8447e5d-3112-4228-9a90-bb710630e9a4",
        'type': "box",
        'visibility': "visible",
        'width': 79,
        'x': 194,
        'y': 260
    },
    {
        'annotated_by': "machine",
        'category': "Right Hand",
        'height': 28,
        'id': "aa76501c-634d-44d0-9574-c15bce512d35",
        'type': "box",
        'visibility': "visible",
        'width': 27,
        'x': 283,
        'y': 107
    }
]

prediction_params = {
    'startFrame': 1,
    'trackedFrameCount': 10,
    'objectId': uuid.uuid4().__str__(),
    'x': 190,
    'y': 245,
    'width': 50,
    'height': 50
}


def next_prediction_params(frame):
    params = {
        'startFrame': frame['frame_num'],
        'trackedFrameCount': 10,
        'objectId': frame['object_id'],
        'x': frame['x'],
        'y': frame['y'],
        'width': frame['width'],
        'height': frame['height']
    }
    return params
