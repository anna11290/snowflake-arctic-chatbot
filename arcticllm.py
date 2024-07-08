import replicate

for event in replicate.stream(
    "snowflake/snowflake-arctic-instruct",
    input={
        "top_k": 50,
        "top_p": 0.9,
        "prompt": "Write fizz buzz in SQL",
        "max_tokens": 512,
        "min_tokens": 0,
        "temperature": 0.2,
        "system_prompt": "You are a helpful assistant.",
        "stop_sequences": "<|im_end|>",
        "presence_penalty": 1.15,
        "frequency_penalty": 0.2
    },
):
    print(str(event), end="")