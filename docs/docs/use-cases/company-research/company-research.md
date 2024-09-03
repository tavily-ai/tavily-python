# Tavily API for  Company Research

## 💡 Why Use Tavily API for Company Research?

Tavily API offers several advantages for conducting in-depth company research:

1. **Comprehensive Data Gathering**: Tavily's advanced search algorithms pull relevant information from a wide range of online sources, providing a robust foundation for in-depth company research. 

2. **Flexible Agentic Search**: When Tavily is integrated into agentic workflows, such as those powered by frameworks like LangGraph, it allows AI agents to dynamically tailor their search strategies. The agents can decide to perform either a news or general search depending on the context, retrieve raw content for more in-depth analysis, or simply pull summaries when high-level insights are sufficient. This adaptability ensures that the research process is optimized according to the specific requirements of the task and the nature of the data available, bringing a new level of autonomy and intelligence to the research process.

3. **Real-time Data Retrieval**: Tavily ensures that the data used for research is up-to-date by querying live sources. This is crucial for company research where timely information can impact the accuracy and relevance of the analysis.

4. **Efficient and Scalable**: Tavily handles multiple queries simultaneously, making it capable of processing large datasets quickly. This efficiency reduces the time needed for comprehensive research, allowing for faster decision-making.

## Example Jupyter Notebook Overview

The following [Jupyter Notebook](https://github.com/tavily-ai/use-cases/blob/main/company-research/company_research.ipynb) demonstrates how to run weekly research process on companies using Tavily API, LangGraph framework, and OpenAI for content generation. This notebook outlines a comprehensive workflow that dynamically gathers relevant information on a company, processes the data, and generates a detailed PDF report.

### Workflow Overview

The notebook utilizes several components to achieve its goal:

1. **ResearchState Setup**:
   - The `ResearchState` data structure manages the company's name, retrieved documents, and the sequence of messages exchanged during the research process. This state keeps track of all necessary data throughout the workflow.

   ```python
   class ResearchState(TypedDict):
       company: str
       report: str
       documents: Dict[str, Dict[Union[str, int], Union[str, float]]]
       messages: Annotated[list[AnyMessage], add_messages]
   ```

2. **Search Query and Data Retrieval**:
    - The `TavilyQuery` and `TavilySearchInput` classes facilitate detailed and efficient searches with the Tavily API. Within an agentic workflow, the agent leverages the Tavily API to determine which queries to execute and under what conditions—choosing the appropriate topic and deciding whether to retrieve raw content for in-depth analysis or summaries for a high-level overview.
      - By appending the current date to the query (e.g., `query_with_date = f"{itm.query} {datetime.now().strftime('%m-%Y')}"`), the agent ensures that the data retrieved by Tavily is current and pertinent.
   ```python
   class TavilyQuery(BaseModel):
       query: str = Field(description="sub query")
       topic: str = Field(description="type of search, should be 'general' or 'news'")
       days: int = Field(description="number of days back to run 'news' search")
       raw_content: bool = Field(description="include raw content from found sources")

    class TavilySearchInput(BaseModel):
        sub_queries: List[TavilyQuery] = Field(description="set of sub-queries that can be answered in isolation")
   ```

   ```python
   @tool("tavily_search", args_schema=TavilySearchInput, return_direct=True)
   async def tavily_search(sub_queries: List[TavilyQuery]):
       # Define a coroutine function to perform a single search with error handling
       async def perform_search(itm):
           query_with_date = f"{itm.query} {datetime.now().strftime('%m-%Y')}"
           response = await tavily_client.search(query=query_with_date, topic=itm.topic, days=itm.days, include_raw_content=itm.raw_content, max_results=10)
           return response['results']
       # Run all the search tasks in parallel
       search_tasks = [perform_search(itm) for itm in sub_queries]
       search_responses = await asyncio.gather(*search_tasks)
       return search_responses
   ```

3. **Tool Execution**:
   - The `tool_node` function handles the execution of search tools, saving the results for later processing. This step is crucial for filtering and organizing the retrieved data before it is used in the final report.

   ```python
   async def tool_node(state: ResearchState):
       docs = state['documents'] or {}
       for tool_call in state["messages"][-1].tool_calls:
           new_docs = await tool.ainvoke(tool_call["args"])
           for doc in new_docs:
               if not docs or doc['url'] not in docs:
                   docs[doc['url']] = doc
       return {"documents": docs}
   ```

4. **Model Invocation and Decision-Making**:
   - The `call_model` function leverages OpenAI as the base model for analyzing and generating insights about the company's latest developments. It also determines the next course of action in the workflow. Depending on the information gathered so far, the model decides whether to continue executing the Tavily tool to gather more data or to proceed directly to writing the report. This decision-making capability is what makes the workflow agentic, allowing it to dynamically adapt to the specific research needs and ensure that the most relevant and comprehensive information is included in the final output.

   ```python
   def call_model(state: ResearchState):
       prompt = f"""Today's date is {datetime.now().strftime('%d/%m/%Y')}.
       You are an expert researcher tasked with preparing a weekly report on recent developments in portfolio companies.
       Your current objective is to gather detailed information about any significant events that occurred in the past week for the following company: {state['company']}.\n
       """
       messages = state['messages'] + [SystemMessage(content=prompt)]
       response = model.invoke(messages)
       return {"messages": [response]}
   ```

   ```python
   def should_continue(state: ResearchState) -> Literal["tools", "write_report"]:
       last_message = state['messages'][-1]
       if last_message.tool_calls:
           return "tools"
       return "write_report"
   ```

5. **Content Generation and Report Writing**:
   - Using OpenAI, the `write_report` function compiles all relevant documents into a detailed, well-written report. The content generation process ensures that the report is thorough and insightful, providing a deep analysis of the company's recent activities. Citations are included to guarantee the reliability of the information presented.

   ```python
   def write_report(state: ResearchState):
       prompt = f"""Today's date is {datetime.now().strftime('%d/%m/%Y')}\n.
       You are an expert researcher, writing a weekly report about recent events in portfolio companies.\n
       Your task is to write an in-depth, well-written, and detailed report on the following company: {state['company']}.\n
       Here are all the documents you gathered so far:\n{state['documents']}\n
       Use only the relevant and most recent documents."""
       response = model.with_structured_output(QuotedAnswer).invoke(messages)
       return {"messages": [AIMessage(content=f"Generated Report:\n{response.answer}")], "report": response.answer}
   ```

6. **PDF Report Creation**:
   - Finally, the `generate_pdf` function converts the generated report into a PDF document. This step makes it easy to share and review the findings in a professional format.

   ```python
   def generate_pdf(state: ResearchState):
       directory = "reports"
       file_name = f"{state['company']} Weekly Report {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
       if not os.path.exists(directory):
           os.makedirs(directory)
       msg = generate_pdf_from_md(state['report'], filename=f'{directory}/{file_name}.pdf')
       return {"messages": [AIMessage(content=msg)]}
   ```

### Conclusion

This notebook showcases a structured approach to automating company research using the Tavily API, LangGraph Agents, and OpenAI for content generation. By following this workflow, you can efficiently gather, process, and present detailed company reports, ensuring that all relevant information is included and accurately represented. The use of agentic workflows, with their dynamic decision-making capabilities, allows the system to adapt to the specific research requirements, making it a powerful tool for continuous company analysis.

You can view examples of company reports generated by the code in the notebook [here](https://github.com/tavily-ai/use-cases/tree/main/company-research/reports).

## Possible Improvements

1. **Real-time Data Filtering and Pre-Content Generation Filtering:** Enhance the workflow by integrating real-time filtering of the retrieved data based on keywords or other relevant criteria. Additionally, incorporating a pre-content generation filtering step, such as selecting the top K most relevant documents, can optimize the Retrieval-Augmented Generation (RAG) process. This approach ensures that only the most pertinent information is used, allowing the content generation step to focus solely on producing high-quality, accurate reports without the burden of additional filtering.

2. **Customized Workflow for Specific Needs:** Tailor the workflow to meet specific requirements by defining a precise report format or prioritizing the use of particular sources. For instance, you can specify that only certain trusted domains should be used for data retrieval or create a structured template that the generated reports must follow. This customization enhances the relevance and precision of the research output, ensuring it aligns closely with your unique needs.
