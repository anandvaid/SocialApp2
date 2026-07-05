
"""
SocialApp2.py
AI Social Media Post Generator (Clean Starter)

This version combines Parts 1 and 2 into a clean structure using the
OpenAI Responses API. It is intended as a solid foundation for future
enhancements.
"""

import json
import pyperclip
import streamlit as st
from openai import OpenAI


st.set_page_config(
    page_title="AI Social Media Post Generator",
    page_icon="🚀",
    layout="wide",
)

st.title("🚀 AI Social Media Post Generator")
st.write("Generate platform-specific social media posts using OpenAI.")

# ---------------- Sidebar ---------------- #

with st.sidebar:
    st.header("Settings")

    api_key = st.text_input("OpenAI API Key", type="password")

    tone = st.selectbox(
        "Writing Tone",
        [
            "Professional",
            "Corporate",
            "Casual",
            "Friendly",
            "Humorous",
            "Sarcastic",
            "Inspirational",
            "Excited",
            "Promotional",
            "Formal",
        ],
    )

    add_emojis = st.checkbox("Add Emojis", value=True)
    generate_hashtags = st.checkbox("Generate Hashtags", value=True)
    generate_image_prompt = st.checkbox("Generate Image Prompt", value=True)
    include_cta = st.checkbox("Include Call-to-Action", value=True)
    mention_date_location = st.checkbox("Mention Date and Location", value=True)
    optimize = st.checkbox("Optimize for Engagement", value=True)

# ---------------- Inputs ---------------- #

st.header("Event Information")

title = st.text_input("Event Title")
description = st.text_area("Event Description", height=180)
event_date = st.text_input("Event Date (Optional)")
location = st.text_input("Event Location (Optional)")
audience = st.text_input("Target Audience (Optional)")
cta = st.text_input("Call-to-Action (Optional)")

platforms = st.multiselect(
    "Select Platforms",
    ["LinkedIn", "Twitter/X", "WhatsApp", "Facebook", "Instagram"],
    default=["LinkedIn", "Twitter/X"],
)

generate = st.button("🚀 Generate Posts", use_container_width=True)


def copy_text(text: str):
    pyperclip.copy(text)
    st.toast("Copied to clipboard!")


if generate:

    if not api_key:
        st.error("Please enter your OpenAI API key.")
        st.stop()

    if not description.strip():
        st.error("Please enter an event description.")
        st.stop()

    if not platforms:
        st.error("Please select at least one platform.")
        st.stop()

    client = OpenAI(api_key=api_key)

    prompt = f"""
Return ONLY valid JSON.

Structure:
{{
 "LinkedIn":{{"post":"","hashtags":""}},
 "Twitter/X":{{"post":"","hashtags":""}},
 "WhatsApp":{{"post":"","hashtags":""}},
 "Facebook":{{"post":"","hashtags":""}},
 "Instagram":{{"post":"","hashtags":""}},
 "image_prompt":""
}}

Generate content ONLY for:
{', '.join(platforms)}

Event Title: {title}
Description: {description}
Date: {event_date}
Location: {location}
Audience: {audience}
CTA: {cta}
Tone: {tone}

Options:
Emojis={add_emojis}
Hashtags={generate_hashtags}
ImagePrompt={generate_image_prompt}
IncludeCTA={include_cta}
MentionDateLocation={mention_date_location}
OptimizeEngagement={optimize}
"""

    try:
        with st.spinner("Generating posts..."):
            response = client.responses.create(
                model="gpt-4.1",
                input=prompt,
            )

        result = json.loads(response.output_text)

    except json.JSONDecodeError:
        st.error("The AI returned invalid JSON. Please try again.")
        st.stop()

    except Exception as e:
        st.error(f"Error: {e}")
        st.stop()

    st.success("Posts generated successfully!")

    all_posts = ""

    for platform in platforms:

        if platform not in result:
            continue

        post = result[platform].get("post", "")
        hashtags = result[platform].get("hashtags", "")
        count = len(post)

        all_posts += (
            f"{platform}\n{'='*40}\n\n"
            f"{post}\n\n{hashtags}\n\n"
        )

        with st.expander(platform, expanded=True):

            st.markdown(post)

            if hashtags:
                st.markdown("### Hashtags")
                st.write(hashtags)

            st.metric("Characters", count)

            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Copy {platform}", key=f"copy_{platform}"):
                    copy_text(post)

            with col2:
                st.download_button(
                    "Download TXT",
                    data=post,
                    file_name=f"{platform}.txt",
                    mime="text/plain",
                    key=f"download_{platform}",
                )

    if generate_image_prompt:
        image_prompt = result.get("image_prompt", "")

        if image_prompt:
            st.header("AI Image Prompt")
            st.code(image_prompt)

            st.download_button(
                "Download Image Prompt",
                image_prompt,
                file_name="image_prompt.txt",
            )

    st.download_button(
        "Download All Posts",
        data=all_posts,
        file_name="all_social_posts.txt",
        mime="text/plain",
    )

    st.header("Summary")

    c1, c2, c3 = st.columns(3)

    c1.metric("Platforms", len(platforms))
    c2.metric("Tone", tone)
    c3.metric("Characters", len(all_posts))
