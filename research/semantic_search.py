import marimo

__generated_with = "0.14.11"
app = marimo.App(width="medium")


@app.cell
def _():
    from sentence_transformers import SentenceTransformer
    from qdrant_client import models, QdrantClient

    return QdrantClient, SentenceTransformer, models


@app.cell
def _():
    import os

    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    return


@app.cell
def _():
    dataset = [
        "rock",
        "rockstar",
        "rocket",
        "rocks",
        "głaz",
        "skała",
        "pies",
        "kamień",
        "kot",
        "szczeniak",
        "firanka",
        "agile",
        "python",
        "hitlet",
        "mussolini",
        "dog",
        "cat",
        "mouse",
    ]
    return (dataset,)


@app.cell
def _(SentenceTransformer):
    model = SentenceTransformer("intfloat/multilingual-e5-large-instruct")
    return (model,)


@app.cell
def _(QdrantClient, dataset, model, models):
    client = QdrantClient(":memory:")

    client.create_collection(
        collection_name="semantic_search",
        vectors_config=models.VectorParams(
            size=model.get_sentence_embedding_dimension(),
            distance=models.Distance.COSINE,
        ),
    )

    client.upload_points(
        collection_name="semantic_search",
        points=[
            models.PointStruct(
                id=idx, vector=model.encode(data).tolist(), payload={"value": data}
            )
            for idx, data in enumerate(dataset)
        ],
    )
    return (client,)


@app.cell
def _():
    match_value = "napoleon"
    return (match_value,)


@app.cell
def _(client, match_value, model):
    hits = client.query_points(
        collection_name="semantic_search",
        query=model.encode(match_value).tolist(),
        limit=6,
    ).points

    for hit in hits:
        print(hit.payload, "score:", hit.score)
    return


if __name__ == "__main__":
    app.run()
