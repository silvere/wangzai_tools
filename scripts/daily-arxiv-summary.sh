#!/bin/bash

# Set variables
SKILL_DIR="/root/clawd/skills/arxiv-paper-reader"
FETCH_SCRIPT="$SKILL_DIR/scripts/fetch-arxiv-papers.py"
SUMMARIZE_SCRIPT="$SKILL_DIR/scripts/summarize-paper.py"
USER_ID="ou_9afed289b1c6420e5b856da29da2eece"
CHANNEL="feishu"

# Fetch recent papers
PAPERS=$(python "$FETCH_SCRIPT" --categories cs.AI cs.CL cs.LG stat.ML --days 7 --max-results 10)

# Parse papers and generate summaries
SUMMARY="# 📚 arXiv 最新大模型 & Agent 论文精选（最近7天）\n\n"
COUNT=0

# Split papers into individual entries
while IFS= read -r line; do
    if [[ "$line" == "--- Paper "* ]]; then
        # Start of new paper
        if [[ -n "$TITLE" && $COUNT -lt 5 ]]; then
            # Generate summary for previous paper
            SUMMARY+="## Paper $COUNT: $TITLE\n"
            SUMMARY+="**Authors**: $AUTHORS\n"
            SUMMARY+="**Published**: $PUBLISHED\n"
            SUMMARY+="**Link**: [PDF]($PDF)\n\n"
            
            # Get structured summary
            SUMMARY_OUTPUT=$(python "$SUMMARIZE_SCRIPT" --title "$TITLE" --abstract "$ABSTRACT")
            if [[ $? -eq 0 ]]; then
                # Parse JSON summary
                MOTIVATION=$(echo "$SUMMARY_OUTPUT" | jq -r '.motivation // "N/A"')
                PROBLEMS=$(echo "$SUMMARY_OUTPUT" | jq -r '.problems // [] | join("\n- ")')
                CONCLUSIONS=$(echo "$SUMMARY_OUTPUT" | jq -r '.conclusions // [] | join("\n- ")')
                
                SUMMARY+="### 研究动机\n$MOTIVATION\n\n"
                
                SUMMARY+="### 核心问题\n"
                if [[ -n "$PROBLEMS" ]]; then
                    SUMMARY+="- $PROBLEMS\n\n"
                else
                    SUMMARY+="暂无\n\n"
                fi
                
                SUMMARY+="### 核心结论\n"
                if [[ -n "$CONCLUSIONS" ]]; then
                    SUMMARY+="- $CONCLUSIONS\n\n"
                else
                    SUMMARY+="暂无\n\n"
                fi
            else
                SUMMARY+="### 摘要\n$ABSTRACT\n\n"
            fi
            SUMMARY+="---\n\n"
        fi
        COUNT=$((COUNT+1))
        TITLE=""
        AUTHORS=""
        PUBLISHED=""
        ABSTRACT=""
        PDF=""
    elif [[ "$line" == "Title: "* ]]; then
        TITLE=${line#Title: }
    elif [[ "$line" == "Authors: "* ]]; then
        AUTHORS=${line#Authors: }
    elif [[ "$line" == "Published: "* ]]; then
        PUBLISHED=${line#Published: }
        # Convert UTC to Beijing time
        PUBLISHED=$(date -d "$PUBLISHED" +"%Y-%m-%d %H:%M:%S" 2>/dev/null || echo "$PUBLISHED")
    elif [[ "$line" == "Abstract: "* ]]; then
        ABSTRACT=${line#Abstract: }
    elif [[ "$line" == "PDF: "* ]]; then
        PDF=${line#PDF: }
    elif [[ -n "$ABSTRACT" ]]; then
        # Continue abstract lines
        ABSTRACT+=" $line"
    fi
done <<< "$PAPERS"

# Add the last paper if we haven't reached 5 yet
if [[ -n "$TITLE" && $COUNT -lt 6 ]]; then
    SUMMARY+="## Paper $COUNT: $TITLE\n"
    SUMMARY+="**Authors**: $AUTHORS\n"
    SUMMARY+="**Published**: $PUBLISHED\n"
    SUMMARY+="**Link**: [PDF]($PDF)\n\n"
    
    SUMMARY_OUTPUT=$(python "$SUMMARIZE_SCRIPT" --title "$TITLE" --abstract "$ABSTRACT")
    if [[ $? -eq 0 ]]; then
        MOTIVATION=$(echo "$SUMMARY_OUTPUT" | jq -r '.motivation // "N/A"')
        PROBLEMS=$(echo "$SUMMARY_OUTPUT" | jq -r '.problems // [] | join("\n- ")')
        CONCLUSIONS=$(echo "$SUMMARY_OUTPUT" | jq -r '.conclusions // [] | join("\n- ")')
        
        SUMMARY+="### 研究动机\n$MOTIVATION\n\n"
        
        SUMMARY+="### 核心问题\n"
        if [[ -n "$PROBLEMS" ]]; then
            SUMMARY+="- $PROBLEMS\n\n"
        else
            SUMMARY+="暂无\n\n"
        fi
        
        SUMMARY+="### 核心结论\n"
        if [[ -n "$CONCLUSIONS" ]]; then
            SUMMARY+="- $CONCLUSIONS\n\n"
        else
            SUMMARY+="暂无\n\n"
        fi
    else
        SUMMARY+="### 摘要\n$ABSTRACT\n\n"
    fi
fi

# Send summary to user
clawdbot message send --channel "$CHANNEL" --target "$USER_ID" --message "$SUMMARY"
