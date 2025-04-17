
# **ultraHumanAPIReader**

Software to download and manage data from the Ultrahuman API.

---

## **Instructions**

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/ultraHumanAPIReader.git
   ```

2. Copy the config file:
   ```bash
   cp config.txt config.yaml
   ```

3. Open `config.yaml` and update the following fields:
   - `datafolder`: Set the folder path where you want the data saved
   - `start_date` and `end_date`: Set your desired date range
   - `email`: Your Ultrahuman account email
   - `key`: Your Ultrahuman API key

4. Run the script:
   ```bash
   python3 dataReader.py
   ```
