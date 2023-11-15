# Welcome to the NannyML Cloud SDK Docs

This page provides an [API reference](api_reference/model.md) for the NannyML Cloud SDK, generated directly from the code. For tutorials and guides, please refer to [our gitbook pages](https://nannyml.gitbook.io/).

## Installing

Currently the package is private, which means you cannot install it via the regular python channels. Instead, you'll have to clone the [repository](https://github.com/NannyML/nannyml-cloud-sdk) and install it from your local copy.

```bash
git clone https://github.com/NannyML/nannyml-cloud-sdk.git
cd nannyml-cloud-sdk
pip install .
```

## Authentication

To use the NannyML Cloud SDK you need to provide the URL of your NannyML Cloud instance and an API token to authenticate. You can obtain an API token on the settings page of your NannyML Cloud instance.

In code:

``` python
import nannyml_cloud_sdk as nml_sdk

nml_sdk.url = "https://beta.app.nannyml.com"
nml_sdk.api_token = r"api token goes here"
```

Using environment variables:

``` python
import nannyml_cloud_sdk as nml_sdk
import os

nml_sdk.url = os.environ['NML_SDK_URL']
nml_sdk.api_token = os.environ['NML_SDK_API_TOKEN']
```

> [!NOTE]
> We recommend using an environment variable for the API token. This prevents accidentally leaking any token associated with your personal account when sharing code.

## Examples

This snippet provides an example of how you can create a model in NannyML Cloud to start monitoring it.

```python
import nannyml_cloud_sdk as nml_sdk
import os
import pandas as pd

nml_sdk.url = os.environ['NML_SDK_URL']
nml_sdk.api_token = os.environ['NML_SDK_API_TOKEN']

# Load a NannyML binary classification dataset to use as example
reference_data = pd.read_csv('https://github.com/NannyML/nannyml/raw/main/nannyml/datasets/data/synthetic_sample_reference.csv')
analysis_data = pd.read_csv('https://github.com/NannyML/nannyml/raw/main/nannyml/datasets/data/synthetic_sample_analysis.csv')
target_data = pd.read_csv('https://github.com/NannyML/nannyml/raw/main/nannyml/datasets/data/synthetic_sample_analysis_gt.csv')
print(reference_data.head())

# Inspect schema from dataset and apply overrides
schema = nml_sdk.Schema.from_df(
    'BINARY_CLASSIFICATION',
    reference_data,
    target_column_name='work_home_actual',
    ignore_column_names=('period'),
)

# Create model
model = nml_sdk.Model.create(
    name='Example model',
    schema=schema,
    chunk_period='MONTHLY',
    reference_data=reference_data,
    analysis_data=analysis_data,
    target_data=target_data,
    main_performance_metric='F1',
)
print("Model", model['id'], "created at", model['createdAt'])
```

!!! note
    The reference dataset is inspected to determine the model schema. NannyML Cloud uses heuristics to automatically identify most columns, but some columns may not be automatically identified. In this case the target column is not identified, so we manually define `work_home_actual` as the target column.

Once a model has been set up in NannyML Cloud, you could use the snippet below to add more data and ensure continuous monitoring of your model.

```python
import nannyml_cloud_sdk as nml_sdk
import os
import pandas as pd

nml_sdk.url = os.environ['NML_SDK_URL']
nml_sdk.api_token = os.environ['NML_SDK_API_TOKEN']

# Find model in NannyML Cloud by name
model, = nml_sdk.Model.list(name='Example model')

# Add new inferences to NannyML Cloud
new_inferences = pd.DataFrame()
nml_sdk.Model.add_analysis_data(model['id'], new_inferences)

# If you have delayed access to ground truth, you can add them to NannyML Cloud
# later. This will match analysis & target datasets using an identifier column.
delayed_ground_truth = pd.DataFrame()
nml_sdk.Model.add_analysis_target_data(model['id'], delayed_ground_truth)

# Trigger analysis of the new data
nml_sdk.Run.trigger(model['id'])
```
