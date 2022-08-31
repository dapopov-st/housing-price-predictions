# Housing price predictions
For a presentation of the work, please see [here](https://drive.google.com/file/d/1i2SVcECHKBUUHEkeb7VoZ_iKitFagROK/view?usp=sharing)

- The aim of this work is to identify the most profitable student housing properties using real estate studies and tree-based models in Python, deploying findings into a Folium+Streamlit+Heroku app for real estate investors.  
- Due to multicollinearity concerns with regularized linear regression, XGBoost, Catboost, and random forest were pooled into the final price prediction
- Cap rates (ratios of net operating income to predicted house price) were used to determine most lucrative properties
- The app is deployed [here](https://ames-app.herokuapp.com/)


![Investing in Real Estate in Ames,Iowa](https://github.com/dapopov-st/housing-price-predictions/blob/main/presentation-and-images/app-image.png)

Special thanks to Varsha Gopalakrishnan, whose phenomenal [blog](https://medium.com/analytics-vidhya/deploying-your-geospatial-machine-learning-projects-as-web-apps-using-streamlit-and-heroku-45d64f6d5cb0)  was instrumental for helping me build the app in reasonable time.
