# dash_streamlit
Prototype of a streamlit dashboard

To see the dashboard, just run the following:

```streamlit run mosqlimate.py```

That's the first view of the dashboard:

<img width="1425" alt="Screen Shot 2023-09-30 at 12 49 46" src="https://github.com/Mosqlimate-project/dash_streamlit/assets/65051489/b227f764-0742-4382-8584-d30cc06ecf65">

The figure on the left was created using the function `plot_heatmap_single` saved in the `vis.py`. The animation on the right was created using the function `plot_map` saved in the `vis.py`.
This animation is heavy, so running the dashboard the first time can take some time. That must be optimized in the following versions.

Just click over the `models` button in the sidebar to see the second page created. This page intends to be a first draft of how the different forecast models will be plotted.

The page created is shown below:

<img width="1152" alt="Screen Shot 2023-09-30 at 12 50 19" src="https://github.com/Mosqlimate-project/dash_streamlit/assets/65051489/06309601-8a51-484d-8705-25828f82339e">

In the sidebar, the user can select a state and a specific city to see the performance of some forecast models in this city. By now, we can compare the models
in the **northeastern state capitals**.

This first graph, entitled `Cases notified by week` was created using the function `plot_time_series_by_week` saved in the `vis.py`. This function uses the data from the mosqlimate API
to generate the plot.

The second graphic is shown below:

<img width="1047" alt="Screen Shot 2023-09-30 at 12 51 46" src="https://github.com/Mosqlimate-project/dash_streamlit/assets/65051489/95ec803f-59d3-4b5d-b241-c1a2b06aa4dd">

This plot was created using the function `plot_for_altair` saved in the `vis.py`. This plot is interactive, hovering the mouse over some gray line (each line represents the output of a different model) will highlight the confidence interval
of this forecast in the right plot. By now, this plot is created using the data from the `predictions` folder, but it will get the predictions from the API in the future.

Below, we have the following plot:

<img width="562" alt="Screen Shot 2023-09-30 at 12 52 34" src="https://github.com/Mosqlimate-project/dash_streamlit/assets/65051489/ba8acf6e-c44d-4e7f-b96e-4505cdefb682">

This plot was created using the function `plot_error_bar` saved in the `vis.py`. You can select a specific metric error and see the behavior of each model according to this metric.

The last thing added is a select box where the user can select the model's name and see a brief description of it. In the future, it can directly get the description saved in
the mosqlimate models API.

<img width="978" alt="Screen Shot 2023-09-30 at 12 52 55" src="https://github.com/Mosqlimate-project/dash_streamlit/assets/65051489/cbb3cf48-1f9a-4f73-a8d1-044c2c865335">
