import os
import requests
import streamlit as st
import browser_automation as auto

# get_jobs("Software Engineer", location="New York, NY", min_salary=100000, remote=True, schedule_type="full-time")
# api_key="d62231893de7d99101a146a8983ef6e147e617698ee096b5d78ab698963a188a"


def jobs_call(query_url, api_key=None):
    st.info(f"Query URL:\n{query_url}")
    params = {"api_key": api_key} if api_key else None
    job_response = requests.get(query_url, params=params)
    if job_response.status_code != 200:
        st.error(f"Error fetching jobs: {job_response.status_code}\n{job_response.text}")
        return f"Error fetching jobs: {job_response.status_code}\n{job_response.text}"
    if job_response.status_code == 401:
        st.error(f"Unauthorized: Some API error. {job_response.text}")
        return f"{job_response.status_code} Unauthorized: Some API error. {job_response.text}"
    results = job_response.json()
    return results
    
def get_jobs(keywords, location=None, min_salary=None, commute=None, schedule_type=None, exp_level=None, api_key=None, next_page=None):
    if next_page:
        return jobs_call(next_page)
    query = {
        "keywords": f"&q={'+'.join(keywords.split(' '))}",
        "location": f"&location={'+'.join(location.split(' '))}" if location else "",
        "min_salary": min_salary,
        "commute": commute,
        "schedule_type": schedule_type if schedule_type in ["full-time", "part-time", "contract", "internship", "temporary"] else None,
        "exp_level": exp_level if exp_level in ["entry", "mid", "senior", "executive"] else None,
    }
    if commute:
        query["keywords"] = f"{query['keywords']}+{'+'.join(commute)}"
    if min_salary:
        query["keywords"] = f"{query['keywords']}+over+{str(min_salary)}"
    if schedule_type:
        query["keywords"] = f"{query['keywords']}+{schedule_type}"
    if exp_level:
        query["keywords"] = f"{query['keywords']}+{exp_level}+years+experience"

    query_url = f"https://serpapi.com/search.json?engine=google_jobs{query['keywords']}{query['location']}&google_domain=google.com&hl=en&gl=us&api_key={api_key}"
    return jobs_call(query_url)

# Streamlit app for UI
def display_jobs(jobs):
    for job in jobs:
        with st.container(border=True):
            st.subheader(job.get("title", "Job listing"))
            st.write(
                f"{job.get('company_name', 'Company not listed')} · "
                f"{job.get('location', 'Location not listed')}"
            )
            if job.get("detected_extensions"):
                st.write(
                    f"{job['detected_extensions'].get('schedule_type', 'Schedule type not listed')}"
                    f"{' · '+job['detected_extensions'].get('salary') if job['detected_extensions'].get('salary') else ''}"
                )
            st.caption(f"via {job.get('via', 'Job listing source not listed')}")
            if job.get("job_highlights"):
                years_of_experience_item = 0
                while (
                    ("years" or "degree") not in job["job_highlights"][0]["items"][years_of_experience_item].lower() 
                    and job["job_highlights"][0]["title"] == "qualifications"
                    and years_of_experience_item < len(job["job_highlights"][0]["items"]) - 1
                ):  years_of_experience_item += 1
                if "year" in job['job_highlights'][0]['items'][years_of_experience_item]:
                    st.write(f"Qualifications: {job['job_highlights'][0]['items'][years_of_experience_item]}")

            if job.get("description"):
                with st.expander("Job description"):
                    st.write(job["description"])
            else:
                st.warning("No job description available.")
            for option in job.get("apply_options", []):
                link = option.get("link")
                if link:
                    if st.button("Automate Application", key=f"apply_{link}"):
                        auto.apply_to_job(link)
                    st.link_button("View Job Posting", link)
                    break

st.set_page_config(page_title="Job search", page_icon=":material/work:")
st.title("JOBCLICK")
st.markdown("Your dream job is only 3 clicks away!")
st.caption("Powered by [SerpApi](https://serpapi.com/), developed by Andre Austin")

with st.form("job_search"):
    keywords = st.text_input("Job title or keywords", "Software Engineer infrastructure")
    location = st.text_input("Location", "New York, NY")
    min_salary = st.number_input("Minimum salary (USD)", min_value=0, step=10000)
    # Commute type checkboxes
    with st.expander("Commute type", expanded=False):
        remote = st.checkbox("Remote")
        hybrid = st.checkbox("Hybrid")
        onsite = st.checkbox("On-site")
        commute = []
        if remote:
            commute.append("remote")
        if hybrid:
            commute.append("hybrid")
        if onsite:
            commute.append("onsite")
    schedule_type = st.selectbox(
        "Schedule type",
        ["Any", "full-time", "part-time", "contract", "internship", "temporary"],
    )
    exp_level = st.selectbox(
        "Years of experience",
        ["Any"] + [i for i in range(0, 30)],
    )
    api_key = st.text_input(
    "SerpApi API key",
    value=os.getenv("SERPAPI_KEY", ""),
    type="password",
    help="Your key is used only to make this search.",)
    search = st.form_submit_button("Search jobs", type="primary")

if "jobs_response" not in st.session_state:
    st.session_state.jobs_response = None

if search:
        try:
            with st.spinner("Searching for jobs..."):
                st.session_state.jobs_response = get_jobs(
                    keywords,
                    location or None,
                    str(min_salary) if min_salary > 0 else None,
                    commute,
                    None if schedule_type == "Any" else schedule_type,
                    None if exp_level == "Any" else exp_level,
                    os.getenv("SERPAPI_KEY", api_key)
            )
        except Exception as error:
            st.error(f"Error occurred while searching for jobs: {str(error)}")

jobs_response = st.session_state.jobs_response
if isinstance(jobs_response, dict):
    jobs = jobs_response.get("jobs_results", [])
    if jobs:
        display_jobs(jobs)
        next_page = jobs_response.get("serpapi_pagination", {}).get("next")
        if next_page and st.button("Load more jobs"):
            try:
                with st.spinner("Loading more jobs..."):
                    next_page_response = jobs_call(next_page, api_key)
                if isinstance(next_page_response, dict):
                    jobs_response["jobs_results"].extend(
                        next_page_response.get("jobs_results", [])
                    )
                    jobs_response["serpapi_pagination"] = next_page_response.get(
                        "serpapi_pagination", {}
                    )
                    st.rerun()
                else:
                    st.error(str(next_page_response))
            except Exception as error:
                st.error(f"Error occurred while loading more jobs: {str(error)}")
    else:
        st.info("No jobs found. Try changing your search.")
elif jobs_response is None and not search:
    st.info("Search to see matching job listings.")
 