# ETL Graph DB for Building Management System
[![Building GraphDB Visualization - Production](https://github.com/jalalAzhmatkhan/etl-graphdb/actions/workflows/deployment.yml/badge.svg)](https://github.com/jalalAzhmatkhan/etl-graphdb/actions/workflows/deployment.yml)

This is an example ETL repository for a system to extract the Building Management System data, transform it into a structured data, load it into a Graph Database, and visualize it.

:computer: _Data Scientist_: Jalaluddin Al Mursyidy Fadhlurrahman

## Environment
### Production
:bar_chart: Data Visualization: [Click here!](http://103.185.52.183:8503/)

## Tools
- Data Visualization: Streamlit
- Graph Database: Neo4j
- Raw Data Ingestion from PDF: Gemma3 4b via Ollama

## Flowcharts
### General Logic
```mermaid
flowchart LR
    start([Start])
    inputPDF[/PDF File/]
    inputExcel[/Excel File/]
    extract[Extract]
    start-->inputPDF
    start -->inputExcel
    inputPDF-->extract
    inputExcel-->extract
    transform[Transform]
    extract-->transform
    load[Load]
    transform-->load
    graphDB[(Neo4j)]
    load-->graphDB
    ending([End])
    graphDB-->ending
```
### Extraction Logic
#### PDF File
```mermaid
flowchart LR
    start([Start])
    inputPDF[/PDF File/]
    start-->inputPDF
    pdfReader[PDF Reader]
    inputPDF-->|read by|pdfReader
    rawMarkdownPDF[/Markdown File/]
    pdfReader-->|dump to|rawMarkdownPDF
    ending([End])
    rawMarkdownPDF-->ending
```
#### Excel File
```mermaid
flowchart LR
    start([Start])
    inputExcel[/Excel File/]
    start-->inputExcel
    excelReader[Pandas Dataframe]
    inputExcel-->|read by|excelReader
    readC1[Read Data C1]
    readC2[Read Data C2]
    excelReader-->readC1
    excelReader-->readC2
    mergedData[Pandas Dataframe]
    summary(((X)))
    readC1-->summary
    readC2-->summary
    summary-->|merged data C1 & C2|mergedData
    outputCSV[/CSV/]
    mergedData-->|dumped to|outputCSV
    ending([End])
    outputCSV-->ending
```
### Transformation Logic
```mermaid
flowchart LR
    start([Start])
    markdownPDF[/Extracted PDF Markdown/]
    csvExcel[/Extracted CSV from Excel/]
    start-->markdownPDF
    start-->csvExcel
    pdfDataIngestion[Transform to JSON]
    markdownPDF-->pdfDataIngestion
    pandasCSV[Pandas]
    csvExcel-->|loaded to|pandasCSV
    pdfDataIngestion-->|loaded to|pandasCSV
    dataCleansing[Data Cleansing]
    dataMatchMerge[Data Match & Merging]
    pandasCSV-->dataCleansing
    dataCleansing-->dataMatchMerge
    csvOutput[/CSV/]
    dataMatchMerge-->|dumped to|csvOutput
    ending([End])
    csvOutput-->ending
```
