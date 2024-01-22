from settings import *
import pyodbc


def db_connect():
    return pyodbc.connect('Driver={SQL Server};Server=' + sql_server + ';Database=Imagelytics;Trusted_Connection=yes;')


def db_get_models():
    models = []

    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute('SELECT [Id], [Filename] FROM [TrainedModels] WHERE [Available] = 1 ORDER BY [Position]')

    for row in cursor:
        print(row)
        models.append(row)

    conn.close()

    return models


def db_set_model_unavailable(model_id):
    conn = db_connect()

    cursor = conn.execute("UPDATE M SET M.[Available] = 0 FROM [TrainedModels] M WHERE M.[Id] = ?",
                          model_id)
    cursor.commit()

    conn.close()


def db_get_project_images(model_id):
    project_images = []

    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute('SELECT TOP {} I.[Id], I.[ProjectId], I.[Name] '
                   'FROM [ProjectImages] I '
                   'INNER JOIN [Projects] P ON I.ProjectId = P.Id '
                   'WHERE I.[State] = 1 AND P.[ModelId] = {} '
                   'ORDER BY I.[Id]'
                   .format(batch_size, model_id))

    for row in cursor:
        print(row)
        project_images.append(row)

    conn.close()

    return project_images


def db_update_project_images(image_classes):
    conn = db_connect()
    for item in image_classes:
        if len(item) == 6:
            # Change ProjectImage state to 2 (Processed) and updates classes and probabilities
            cursor = conn.execute("UPDATE [ProjectImages] SET [State] = 2, "
                                  "[Class1] = ?, [ClassProbability1] = ?, "
                                  "[Class2] = ?, [ClassProbability2] = ?, "
                                  "[Class3] = ?, [ClassProbability3] = ?, "
                                  "[Class4] = ?, [ClassProbability4] = ?, "
                                  "[Class5] = ?, [ClassProbability5] = ? WHERE [Id] = ?",
                                  item[1][0], item[1][1],
                                  item[2][0], item[2][1],
                                  item[3][0], item[3][1],
                                  item[4][0], item[4][1],
                                  item[5][0], item[5][1], item[0])
            cursor.commit()
        else:
            # Change ProjectImage state to 3 (Error)
            cursor = conn.execute("UPDATE [ProjectImages] SET [State] = 3 WHERE [Id] = ?", item[0])
            cursor.commit()

    # Change state to all projects in progress (State = 2) to finished (State = 3) if all images processed (State <> 1)
    query = "UPDATE P SET P.[State] = 3 FROM [Projects] P WHERE P.[State] = 2 AND " \
            "(SELECT COUNT(*) FROM [ProjectImages] PI WHERE PI.[ProjectId] = P.[Id] AND PI.[State] = 1) = 0"
    cursor = conn.execute(query)
    cursor.commit()

    conn.close()
