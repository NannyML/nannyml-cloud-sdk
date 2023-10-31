<p align="center">
    <img src="media/thumbnail-4.png">
</p>

# 💡 Introduction

NannyML Cloud is a web application that allows you to **estimate post-deployment model performance** (without access to targets), detect data drift, and intelligently link data drift alerts back to changes in model performance. Built for data scientists, NannyML Cloud has an easy-to-use interface, interactive visualizations, is completely model-agnostic and currently supports all tabular use cases, classification and **regression**.

NannyML Cloud SDK is a python package that allows you to programatically interact with NannyML Cloud.

Some example use cases:

- Creating a model for monitoring
- Logging inferences for analysis
- Triggering model analysis


# 🔨 Development

## 🤖 API code generation

The API interface to interact with NannyML Cloud is generated from a GraphQL schema.

To extend or update the API interface:

1. Ensure the schema in [graphql/schema.graphql](graphql/schema.graphql) is up to date.
2. Add (or updates) queries in [graphql/queries/](graphql/queries/).
3. Run `make graphql-cg` to regenerate the API interface.
