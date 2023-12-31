import streamlit as st
import modal
import json
import os
from io import BytesIO


def main():
    st.title("Personal Podcast Overview 📻")
    st.divider()
    available_podcast_info = create_dict_from_json_files(".")

    # Left section - Input fields
    st.sidebar.header("Podcast RSS Feeds")

    # Dropdown box
    st.sidebar.subheader("Available Podcasts Feeds")
    selected_podcast = st.sidebar.selectbox(
        "Select Podcast",
        options=["Process new episode"] + list(available_podcast_info.keys()),
    )

    if selected_podcast != "Process new episode":
        podcast_info = available_podcast_info[selected_podcast]

        # Display the podcast summary and the cover image in a side-by-side layout
        col1, col2 = st.columns([8, 3])

        with col1:
            # Display the podcast title
            episode_title = podcast_info["podcast_details"]["episode_title"]
            st.subheader(f":red[Latest Episode] 🌱 \n **{episode_title}**")

            guest = podcast_info["podcast_guest"]
            st.subheader(f":red[Guest] : _{guest}_")
            podcast_info["podcast_guest_info"]

        with col2:
            st.image(
                podcast_info["podcast_details"]["episode_image"],
                caption="Podcast Cover",
                width=300,
                use_column_width=True,
            )
        # Display the podcast episode summary
        st.subheader(":red[Summary] 📬")
        st.write(podcast_info["podcast_summary"])
        st.divider()

        with st.expander("📍 :blue[**More from this episode**]"):
            # Display the key moments
            """"""
            st.markdown("💫 :blue[**Highlights**]")
            podcast_info["podcast_highlights"]
            ""
            st.markdown("📝 :blue[**Insides**]")
            podcast_info["podcast_insights"]
            ""
            st.markdown("🤗 **:blue[Recommendations]**")
            podcast_info["podcast_actionable_recommendations"]

    else:
        # User Input box
        st.sidebar.subheader("Add and Process New Podcast Feed")
        url = st.sidebar.text_input("Link to RSS Feed")

        process_button = st.sidebar.button("Process Podcast Feed")
        st.sidebar.markdown(
            "**Note**: Podcast processing can take upto 5 mins, please be patient."
        )

        if process_button:
            st.empty()
            # Call the function to process the URLs and retrieve podcast guest information
            podcast_info = process_podcast_info(url)

            # Display the podcast summary and the cover image in a side-by-side layout
            col1, col2 = st.columns([8, 3])

            with col1:
                # Display the podcast title
                episode_title = podcast_info["podcast_details"]["episode_title"]
                st.subheader(f":red[Latest Episode] 🌱 \n **{episode_title}**")

                guest = podcast_info["podcast_guest"]
                st.subheader(f":red[Guest] : _{guest}_")
                podcast_info["podcast_guest_info"]

            with col2:
                st.image(
                    podcast_info["podcast_details"]["episode_image"],
                    caption="Podcast Cover",
                    width=300,
                    use_column_width=True,
                )
            # Display the podcast episode summary
            st.subheader(":red[Summary] 📬")
            st.write(podcast_info["podcast_summary"])
            st.divider()

            with st.expander("📍 :blue[**More from this episode**]"):
                # Display the key moments
                """"""
                st.markdown("💫 :blue[**Highlights**]")
                podcast_info["podcast_highlights"]
                ""
                st.markdown("📝 :blue[**Insides**]")
                podcast_info["podcast_insights"]
                ""
                st.markdown("🤗 **:blue[Recommendations]**")
                podcast_info["podcast_actionable_recommendations"]


def create_dict_from_json_files(folder_path):
    json_files = [f for f in os.listdir(folder_path) if f.endswith(".json")]
    data_dict = {}

    for file_name in json_files:
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, "r") as file:
            podcast_info = json.load(file)
            podcast_name = podcast_info["podcast_details"]["podcast_title"]
            # Process the file data as needed
            data_dict[podcast_name] = podcast_info

    return data_dict


def process_podcast_info(url):
    f = modal.Function.lookup("corise-podcast-project", "process_podcast")
    output = f.remote(url, "/content/podcast/")
    return output


if __name__ == "__main__":
    main()
