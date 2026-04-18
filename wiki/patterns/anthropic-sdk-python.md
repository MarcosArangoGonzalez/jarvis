---
title: "anthropic-sdk-python"
type: source
status: draft
tags:
  - "github"
  - "api-client"
  - "python"
  - "docker"
  - "development"
created: 2026-04-18
updated: 2026-04-18
tokens_consumed: 145
sources:
  - "https://github.com/anthropics/anthropic-sdk-python"
Summary: "A Python client library for interacting with the Anthropic Claude AI system."
requires_verification: true
---

# anthropic-sdk-python

> A Python client library for interacting with the Anthropic Claude AI system.

## Source

- URL: https://github.com/anthropics/anthropic-sdk-python
- Type: github
- Domain: ai

## Raw Extract (excerpt)

## Languages
Python, Shell, Dockerfile, Ruby

## README
# Claude SDK for Python

[![PyPI version](https://img.shields.io/pypi/v/anthropic.svg)](https://pypi.org/project/anthropic/)

The Claude SDK for Python provides access to the [Claude API](https://docs.anthropic.com/en/api/) from Python applications.

## Documentation

Full documentation is available at **[platform.claude.com/docs/en/api/sdks/python](https://platform.claude.com/docs/en/api/sdks/python)**.

## Installation

```sh
pip install anthropic
```

## Getting started

```python
import os
from anthropic import Anthropic

client = Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),  # This is the default and can be omitted
)

message = client.messages.create(
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Hello, Claude",
        }
    ],
    model="claude-opus-4-6",
)
print(message.content)
```

## Requirements

Python 3.9+

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

