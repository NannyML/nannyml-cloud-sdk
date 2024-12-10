# Welcome to the NannyML Cloud SDK Docs

This page provides an [API reference](api_reference/monitoring/model.md) for the NannyML Cloud SDK, generated directly from the code. For tutorials and guides, please refer to [our gitbook pages](https://nannyml.gitbook.io/).

### Install NannyML Cloud SDK

The nannyml-cloud-sdk package is available on PyPi and can be installed using your favorite package manager. 

### Compatibility

You can check which SDK version support which NannyML Cloud versions over on the [dedicated cloud documentation page](https://docs.nannyml.com/cloud/nannyml-cloud-sdk/getting-started#compatibility).

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

!!! note
    We recommend using an environment variable for the API token. This prevents accidentally leaking any token associated with your personal account when sharing code.

## Examples

### Model monitoring

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
schema = nml_sdk.monitoring.Schema.from_df(
    'BINARY_CLASSIFICATION',
    reference_data,
    target_column_name='work_home_actual',
    ignore_column_names=('period'),
)

# Create model
model = nml_sdk.monitoring.Model.create(
    name='Example model',
    schema=schema,
    chunk_period='MONTHLY',
    reference_data=reference_data,
    analysis_data=analysis_data,
    target_data=target_data,
    key_performance_metric='F1',
)

# Tweak some settings
config = nml_sdk.monitoring.RuntimeConfiguration.get(model['id'])
config.performance_metric('ACCURACY').enable_realized().enable_estimated()
config.performance_metric('ROC_AUC').set_threshold(threshold_type='CONSTANT', lower=0.7, upper=0.9)
config.univariate_drift_method('WASSERSTEIN').enable_targets()

nml_sdk.monitoring.RuntimeConfiguration.set(model['id'], config)

print("Model", model['id'], "created at", model['createdAt'])

# Start running the model
nml_sdk.monitoring.Run.trigger(model['id'])
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
model, = nml_sdk.monitoring.Model.list(name='Example model')

# Add new inferences to NannyML Cloud
new_inferences = pd.DataFrame()
nml_sdk.monitoring.Model.add_analysis_data(model['id'], new_inferences)

# If you have delayed access to ground truth, you can add them to NannyML Cloud
# later. This will match analysis & target datasets using an identifier column.
delayed_ground_truth = pd.DataFrame()
nml_sdk.monitoring.Model.add_analysis_target_data(model['id'], delayed_ground_truth)

# Trigger analysis of the new data
nml_sdk.monitoring.Run.trigger(model['id'])
```


### Model evaluation

This snippet provides an example of how you can set up model evaluation in NannyML Cloud.

You can configure each of the available performance metrics by providing an optional value for ROPE and HDI width.
If a `None` is provided, NannyML will calculate a sensible default during the first evaluation run.

```python
import nannyml_cloud_sdk as nml_sdk
import os
import pandas as pd

nml_sdk.url = os.environ['NML_SDK_URL']
nml_sdk.api_token = os.environ['NML_SDK_API_TOKEN']

# Load a NannyML binary classification dataset to use as example
reference_data = pd.read_csv('https://github.com/NannyML/nannyml/raw/main/nannyml/datasets/data/synthetic_car_loan_reference.csv')
analysis_data = pd.read_csv('https://github.com/NannyML/nannyml/raw/main/nannyml/datasets/data/synthetic_car_loan_analysis.csv')
target_data = pd.read_csv('https://github.com/NannyML/nannyml/raw/main/nannyml/datasets/data/synthetic_car_loan_analysis_target.csv')

# The evaluation data will be a combination of analysis and target datasets. We'll only use the first 1000 rows for now.
evaluation_data = analysis_data.merge(target_data, on='id').head(1000)

print(reference_data.head())

# Inspect schema from dataset and apply overrides
schema = nml_sdk.model_evaluation.Schema.from_df(
    'BINARY_CLASSIFICATION',
    reference_data,
    target_column_name='repaid',
)

# Create model
model = nml_sdk.model_evaluation.Model.create(
    name='from_sdk',
    schema=schema,
    reference_data=reference_data,
    evaluation_data=evaluation_data,
    metrics_configuration={
        'F1': {
            'enabled': True,
            'rope_lower_bound': 0.8,
            'rope_upper_bound': 0.9,
            'hdi_width': 0.01
        },
        'ACCURACY': {
            'enabled': True,
            'rope_lower_bound': None,
            'rope_upper_bound': None,
            'hdi_width': None
        },
    },
    key_performance_metric='F1',
    hypothesis='MODEL_PERFORMANCE_NO_WORSE_THAN_REFERENCE',
    classification_threshold=0.5,
)
print("Model", model['id'], "created at", model['createdAt'])

# Now trigger the model evaluation run with our first 1000 rows of evaluation data

nml_sdk.model_evaluation.Run.trigger(model['id'])
```

Now we'll add the next set of evaluation data and trigger another evaluation run.

```
import nannyml_cloud_sdk as nml_sdk
import os
import pandas as pd

evaluation_data = analysis_data.join(target_data, on='id').iloc[1000:2000]

# Retrieve the model that was created earlier, using the name as a filter.
model, = nml_sdk.model_evaluation.Model.list(name='from_sdk')
print(model)

# Adding the new evaluation data to the model
nml_sdk.model_evaluation.Model.add_evaluation_data(model_id=model['id'], data=evaluation_data)

# Trigger the model evaluation run to include the latest set of evaluation data
nml_sdk.model_evaluation.Run.trigger(model['id'])
```

### Experiments

This snippet provides an example of how you can set up an A/B-testing experiment in NannyML Cloud.

You can configure each of the available metrics by providing a value for ROPE and HDI width.

```python
import nannyml_cloud_sdk as nml_sdk
from pprint import pprint
import pandas as pd
import os

nml_sdk.url = os.environ['NML_SDK_URL']
nml_sdk.api_token = os.environ['NML_SDK_API_TOKEN']

experiment_data = pd.DataFrame({
    'variable': ['RJ45', 'RJ45', 'FOO', 'FOO'],
    'group': ['control', 'treatment', 'control', 'treatment'],
    'success_count': [50, 30, 25, 10],
    'fail_count': [1, 2, 2, 0],
    'random': [1, 2, 5, 7],
})

metrics = list(experiment_data['variable'].unique())

schema = nml_sdk.experiment.Schema.from_df(df=experiment_data, metric_column_name='variable')
pprint(schema)

experiment = nml_sdk.experiment.Experiment.create(
    name='experiment (SDK)',
    schema=schema,
    experiment_type='A_B_TESTING',
    experiment_data=experiment_data,
    key_experiment_metric='renewed',
    metrics_configuration={
        metric: {
            "rope_lower_bound": 0.80,
            "rope_upper_bound": 0.90,
            "hdi_width": 0.01,
            "enabled": True,
        } for metric in metrics
    }
)
pprint(experiment)

nml_sdk.experiment.Run.trigger(experiment['id'])
```

Now we'll add the next set of experiment data and trigger another evaluation run.

```python
import nannyml_cloud_sdk as nml_sdk
import os
import pandas as pd

nml_sdk.url = os.environ['NML_SDK_URL']
nml_sdk.api_token = os.environ['NML_SDK_API_TOKEN']

experiment_data = pd.DataFrame({
    'variable': ['RJ45', 'RJ45', 'FOO', 'FOO'],
    'group': ['control', 'treatment', 'control', 'treatment'],
    'success_count': [27, 35, 19, 31],
    'fail_count': [1, 5, 12, 12],
    'random': [1, 2, 5, 7],
})

experiment, = nml_sdk.experiment.Experiment.list(name='experiment (SDK)')

nml_sdk.experiment.Experiment.add_experiment_data(experiment['id'], experiment_data)

nml_sdk.experiment.Run.trigger(experiment['id'])
```
