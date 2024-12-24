<!DOCTYPE html>
<html>
<head>
    <title>PDF Document Processor</title>
    <style>
        .container {
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
            border-radius: 8px;
        }
        .response {
            margin-top: 20px;
            padding: 15px;
            background: #fff;
            border-radius: 4px;
            display: none;
        }
        .status {
            margin-top: 10px;
            padding: 10px;
            background: #e8f4f8;
            border-radius: 4px;
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>PDF Document Processor</h2>
        <form id="uploadForm" enctype="multipart/form-data">
            <input type="file" name="file" accept=".pdf" required>
            <button type="submit">Process Document</button>
        </form>
        <div id="status" class="status"></div>
        <div id="response" class="response"></div>
    </div>

    <script>
        async function checkStatus(taskId) {
            try {
                const response = await fetch(`http://localhost:8000/status/${taskId}`);
                const data = await response.json();
                
                const statusDiv = document.getElementById('status');
                statusDiv.style.display = 'block';
                statusDiv.innerHTML = `Status: ${data.status}`;
                
                if (data.status === 'completed') {
                    document.getElementById('response').style.display = 'block';
                    document.getElementById('response').innerHTML = `<p>Processing Result: ${data.result}</p>`;
                    return true;
                } else if (data.status === 'failed') {
                    document.getElementById('response').style.display = 'block';
                    document.getElementById('response').innerHTML = `<p>Error: ${data.error}</p>`;
                    return true;
                }
                return false;
            } catch (error) {
                console.error('Error checking status:', error);
                return false;
            }
        }

        document.getElementById('uploadForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const statusDiv = document.getElementById('status');
            const responseDiv = document.getElementById('response');
            
            statusDiv.style.display = 'block';
            statusDiv.innerHTML = 'Uploading...';
            responseDiv.style.display = 'none';
            
            try {
                const response = await fetch('http://localhost:9000/process-document/', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const result = await response.json();
                const taskId = result.task_id;
                
                statusDiv.innerHTML = 'Processing...';
                
                // Poll for status every 2 seconds
                const pollInterval = setInterval(async () => {
                    const isComplete = await checkStatus(taskId);
                    if (isComplete) {
                        clearInterval(pollInterval);
                    }
                }, 2000);
                
            } catch (error) {
                responseDiv.style.display = 'block';
                responseDiv.innerHTML = `<p>Error: ${error.message}</p>`;
                console.error('Error:', error);
            }
        });
    </script>
</body>
</html>