alert('something')
console.log('working')
const siteUrl = 'http://127.0.0.1:8000/';
const styleUrl = siteUrl + 'static/css/bookmarklet.css';
const minWidth = 100;
const minHeight = 100;

// ২. CSS লোড করা
var head = document.getElementsByTagName('head')[0];
var link = document.createElement('link');
link.rel = 'stylesheet';
link.type = 'text/css';
link.href = styleUrl + '?r=' + Math.floor(Math.random()*9999999999999999);
head.appendChild(link);

// ৩. HTML ইনজেক্ট করা (innerHTML += এর বদলে insertAdjacentHTML ব্যবহার করা নিরাপদ)
var body = document.getElementsByTagName('body')[0];
var boxHtml = `
  <div id="bookmarklet">
    <a href="#" id="close" onclick="document.getElementById('bookmarklet').style.display='none'; return false;">&times;</a>
    <h1>Select an image to bookmark:</h1>
    <div class="images"></div>
  </div>`;
body.insertAdjacentHTML('beforeend', boxHtml);

function bookmarkletLaunch() {
    var bookmarklet = document.getElementById('bookmarklet');
    var imagesFound = bookmarklet.querySelector('.images');
    imagesFound.innerHTML = ''; 
    bookmarklet.style.display = 'block';

    // সাইটের সব ইমেজ খুঁজে দেখা
    var images = document.querySelectorAll('img');
    images.forEach(image => {
        // naturalWidth সরাসরি অনেক সময় পাওয়া যায় না, তাই চেক করা ভালো
        if(image.naturalWidth >= minWidth && image.naturalHeight >= minHeight) {
            var resizableImage = document.createElement('img');
            resizableImage.src = image.src;
            imagesFound.append(resizableImage);
        }
    });

    // ছবিতে ক্লিক করলে আপনার সাইটে রিডাইরেক্ট করা
    imagesFound.querySelectorAll('img').forEach(image => {
        image.addEventListener('click', function(event){
            var imageSelected = event.target;
            bookmarklet.style.display = 'none';
            window.open(siteUrl + 'image/create/?url='
                        + encodeURIComponent(imageSelected.src)
                        + '&title='
                        + encodeURIComponent(document.title),
                        '_blank');
        });
    });
}

// ফাংশন কল করা
bookmarkletLaunch();