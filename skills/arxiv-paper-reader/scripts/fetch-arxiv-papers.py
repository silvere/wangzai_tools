#!/usr/bin/env python3
"""
Fetch and summarize recent arXiv papers in specified categories.
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import argparse
import json

def fetch_arxiv_papers(categories, days=3, max_results=10):
    """Fetch recent arXiv papers from specified categories."""
    base_url = "http://export.arxiv.org/api/query"
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Format dates for arXiv API (YYYYMMDDHHMMSS)
    start_date_str = start_date.strftime("%Y%m%d%H%M%S")
    end_date_str = end_date.strftime("%Y%m%d%H%M%S")
    
    # Build category query
    category_query = " OR ".join([f"cat:{cat}" for cat in categories])
    
    params = {
        "search_query": f"({category_query}) AND submittedDate:[{start_date_str} TO {end_date_str}]",
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": max_results
    }
    
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    
    return response.text

def parse_arxiv_xml(xml_content):
    """Parse arXiv XML response into structured data."""
    ns = {"arxiv": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(xml_content)
    
    papers = []
    for entry in root.findall("arxiv:entry", ns):
        paper = {}
        
        # Basic metadata
        paper["title"] = entry.find("arxiv:title", ns).text.strip()
        paper["id"] = entry.find("arxiv:id", ns).text
        paper["published"] = entry.find("arxiv:published", ns).text
        paper["updated"] = entry.find("arxiv:updated", ns).text
        
        # Authors
        authors = []
        for author in entry.findall("arxiv:author", ns):
            name = author.find("arxiv:name", ns).text
            authors.append(name)
        paper["authors"] = authors
        
        # Abstract
        abstract = entry.find("arxiv:summary", ns).text
        paper["abstract"] = abstract.strip() if abstract else ""
        
        # Categories
        categories = []
        for cat in entry.findall("arxiv:category", ns):
            categories.append(cat.attrib["term"])
        paper["categories"] = categories
        
        # Links
        links = {}
        for link in entry.findall("arxiv:link", ns):
            if link.attrib.get("title") == "pdf":
                links["pdf"] = link.attrib["href"]
            elif link.attrib.get("rel") == "alternate":
                links["html"] = link.attrib["href"]
        paper["links"] = links
        
        papers.append(paper)
    
    return papers

def generate_summary(paper):
    """Generate structured summary for a paper."""
    # For now, we'll use the abstract as the base
    # In a real implementation, this could use an LLM to extract key points
    summary = {
        "title": paper["title"],
        "authors": ", ".join(paper["authors"]),
        "published": paper["published"],
        "abstract": paper["abstract"],
        "links": paper["links"],
        "categories": paper["categories"],
        # These fields would be populated by an LLM in a real implementation
        "research_motivation": "",
        "research_hypothesis": "",
        "key_problems": [],
        "key_conclusions": [],
        "usage_guide": ""
    }
    
    return summary

def main():
    parser = argparse.ArgumentParser(description="Fetch recent arXiv papers")
    parser.add_argument("--categories", nargs="+", default=["cs.AI", "cs.CL", "cs.LG"],
                       help="arXiv categories to search (default: cs.AI cs.CL cs.LG)")
    parser.add_argument("--days", type=int, default=3,
                       help="Number of days to look back (default: 3)")
    parser.add_argument("--max-results", type=int, default=10,
                       help="Maximum number of results to fetch (default: 10)")
    parser.add_argument("--output", help="Output file path (JSON format)")
    
    args = parser.parse_args()
    
    try:
        print(f"Fetching papers from categories: {', '.join(args.categories)}")
        print(f"Looking back {args.days} days...")
        
        xml_content = fetch_arxiv_papers(args.categories, args.days, args.max_results)
        papers = parse_arxiv_xml(xml_content)
        
        print(f"Found {len(papers)} papers")
        
        # Generate summaries
        summaries = [generate_summary(paper) for paper in papers]
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(summaries, f, indent=2)
            print(f"Summaries saved to {args.output}")
        else:
            # Print to console
            for i, summary in enumerate(summaries, 1):
                print(f"\n--- Paper {i} ---")
                print(f"Title: {summary['title']}")
                print(f"Authors: {summary['authors']}")
                print(f"Published: {summary['published']}")
                print(f"Abstract: {summary['abstract'][:300]}...")
                print(f"PDF: {summary['links'].get('pdf', 'N/A')}")
        
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
