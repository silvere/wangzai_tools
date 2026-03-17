#!/bin/bash
# memsearch wrapper using Ark embedding via local proxy
export OPENAI_API_KEY="dummy"
export OPENAI_BASE_URL="http://127.0.0.1:18765/v1"
memsearch "$@"
