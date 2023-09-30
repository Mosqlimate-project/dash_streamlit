# dash_streamlit
Prototype of a streamlit dashboard

To see the dashboard, just run the following:

```streamlit run mosqlimate.py```

That's the first view of the dashboard:
<img width="1424" alt="Screen Shot 2023-09-30 at 12 21 50" src="https://github.com/Mosqlimate-project/dash_streamlit/assets/65051489/cd70e687-208b-45da-ac0c -9f7520c42cd9">

The figure on the left was created using the function `plot_heatmap_single` saved in the `vis.py`. The animation on the right was created using the function `plot_map` saved in the `vis.py`.
This animation is heavy, so running the dashboard the first time can take some time. That must be optimized in the following versions.

Just click over the `models` button in the sidebar to see the second page created. This page intends to be a first draft of how the different forecast models will be plotted.

The page created is shown below:

<img width="1183" alt="Screen Shot 2023-09-30 at 12 28 07" src="https://github.com/Mosqlimate-project/dash_streamlit/assets/65051489/0f6b93d0-cd67-4640-8013 -6e2c6bafad29">

In the sidebar, the user can select a state and a specific city to see the performance of some forecast models in this city. By now, we can compare the models
in the **northeastern state capitals**.

This first graph, entitled `Cases notified by week` was created using the function `plot_time_series_by_week` saved in the `vis.py`. This function uses the data from the mosqlimate API
to generate the plot.

The second graphic is shown below:

<img width="1059" alt="Screen Shot 2023-09-30 at 12 35 56" src="https://github.com/Mosqlimate-project/dash_streamlit/assets/65051489/d135ce0c-1030-4512-8de2 -d569942f2788">

This plot was created using the function `plot_for_altair` saved in the `vis.py`. This plot is interactive, hovering the mouse over some gray line (each line represents the output of a different model) will highlight the confidence interval
of this forecast in the right plot. By now, this plot is created using the data from the `predictions` folder, but it will get the predictions from the API in the future.

Below, we have the following plot:
<img width="580" alt="Screen Shot 2023-09-30 at 12 39 19" src="https://github.com/Mosqlimate-project/dash_streamlit/assets/65051489/5aa30d8c-d1e1-4d31-a155 -2798378f2c92">

This plot was created using the function `plot_error_bar` saved in the `vis.py`. You can select a specific metric error and see the behavior of each model according to this metric.

The last thing added is a select box where the user can select the model's name and see a brief description of it. In the future, it can directly get the description saved in
the mosqlimate models API.

<img width="983" alt="Screen Shot 2023-09-30 at 12 41 55" src="https://github.com/Mosqlimate-project/dash_streamlit/assets/65051489/d44e4289-33e3-4cb9-b105 -0a3b181feb23">

