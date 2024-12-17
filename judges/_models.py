from openai import OpenAI

def get_available_models():
    client = OpenAI()

    models = []
    oai_models = client.models.list()
    for model in oai_models.data:
        models.append({"client": "openai", "name": model.id})

    try:
        import litellm
    except ImportError:
        pass
    else:
        litellm_models = litellm.model_list
        for model in litellm_models:
            models.append({"client": "litellm", "name": model})

    models = sorted(models, key=lambda x: (x["client"], x["name"]))
    return models
