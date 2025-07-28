#!/usr/bin/env python3
"""Example of how to save research reports to disk"""

import asyncio
import os
from datetime import datetime
from pathlib import Path
from langchain_core.messages import HumanMessage
from open_deep_research.deep_researcher import deep_researcher

async def run_research_and_save(query: str, output_dir: str = "research_reports"):
    """Run research and save the report to disk"""
    
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Run the research
    print(f"Researching: {query}")
    result = await deep_researcher.ainvoke({
        "messages": [HumanMessage(content=query)]
    })
    
    # Get the final report
    if "final_report" in result and result["final_report"]:
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"research_report_{timestamp}.md"
        filepath = os.path.join(output_dir, filename)
        
        # Save the report
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# Research Report\n\n")
            f.write(f"**Query**: {query}\n\n")
            f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            f.write(result["final_report"])
        
        print(f"\n✅ Report saved to: {filepath}")
        return filepath
    else:
        print("\n❌ No final report generated")
        return None

if __name__ == "__main__":
    # Example usage
    query = "What are the latest developments in quantum computing?"
    asyncio.run(run_research_and_save(query))