// Handle text submission
document.getElementById('textForm').addEventListener('submit', async function (e) {
    e.preventDefault();
    let textInput = document.getElementById('text-input').value;
    let response = await fetch('/text_to_video', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: textInput })
    });

    let result = await response.json();
    
    // Check if video file is available
    if (result.video_file) {
        document.getElementById('summaryText').innerText = result.summary; // Set the summary
        document.getElementById('videoSource').src = result.video_file; // Set the video source
        document.getElementById('videoPlayer').load(); // Load the new video
    } else {
        alert('Error generating video: ' + result.error); // Handle errors
    }
});

// Handle YouTube URL submission
document.getElementById('youtubeForm').addEventListener('submit', async function (e) {
    e.preventDefault();
    let youtubeUrl = document.getElementById('youtube-url').value;
    let response = await fetch('/youtube_to_text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: youtubeUrl })
    });

    let result = await response.json();
    
    // Check if transcript and summary are available
    if (result.summary) {
        document.getElementById('summaryText').innerText = result.summary; // Set the summary
        document.getElementById('videoSource').src = '';  // Clear previous video
        document.getElementById('videoPlayer').load(); // Reload the video player
    } else {
        alert('Error fetching summary: ' + result.error); // Handle errors
    }
});
