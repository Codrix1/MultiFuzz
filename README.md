
# MultiFuzz

MultiFuzz is a smart and efficient Multi-Agent System for network protocol fuzzing, leveraging AI Agents combined with dense retrieval.

## Tech Stack

**Server:** FastAPI

**AI & RAG:** CrewAI + Langchain + ChromaDB



## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`OPENAI_API_KEY`: For the embedding model, which is ` text-embedding-ada-002`

`GROQ_API_KEY`: For LLMs inference, obtain from [Groq Cloud Console](https://console.groq.com/)

`AGENTOPS_API_KEY`: For agents monitoring, obtain from [AgentOps](https://www.agentops.ai/)


## Run Locally

Note: Ensure that you have [Docker](https://www.docker.com/) installed for container management.

Clone the project

```bash
  git clone https://github.com/Codrix1/MultiFuzz
```

Go to the project directory:

```bash
  cd MultiFuzz/crew-api/crew-api
```

Install dependencies in a python virtual environment:

```bash
  python -m venv venv
  .\venv\Scripts\activate
  pip install -r requirements.txt
```

Start the FastAPI server

```bash
  python main.py
```

Now you can test the API Endpoints using [Postman](https://www.postman.com/) or, an easy, yet fast alternative, open browser and go to the auto-generated FastAPI's SwaggerUI for api testing in:

```bash
http://localhost:8000/docs
```

Containerize the Crew of agents api by building the Dockerfile:

```bash
docker build . -t crew-api
```

In docker terminal, create a docker network to call the crew-api from an isolated container with port mapping:

```bash
docker network create fuzznet
docker run -d --network fuzznet -p 8000:8000 --name llm-server crew-api
```

To run ChatAFL using the created network in isolation reaching the llm-server, replace the ChatAFL-master\benchmark\scripts\execution\profuzzbench_exec_common.sh file part, which is: 

```bash
for i in $(seq 1 $RUNS); do
  id=$(docker run --cpus=1 -d -it $DOCIMAGE /bin/bash -c "cd ${WORKDIR} && run ${FUZZER} ${OUTDIR} '${OPTIONS}' ${TIMEOUT} ${SKIPCOUNT}")
  cids+=(${id::12}) #store only the first 12 characters of a container ID
done
```

and make it:

```bash
for i in $(seq 1 $RUNS); do
  id=$(docker run --cpus=1 -d -it --network fuzznet $DOCIMAGE /bin/bash -c "cd ${WORKDIR} && run ${FUZZER} ${OUTDIR} '${OPTIONS}' ${TIMEOUT} ${SKIPCOUNT}")
  cids+=(${id::12})
done
```

Now follow ChatAFL's README, to run the fuzzer.


## Authors

- [@YoussefMaklad](https://www.github.com/YoussefMaklad)
- [@Codrix1](https://github.com/Codrix1)
