

const reveals = document.querySelectorAll('.reveal');
const options = {
    threshold: 0.1
};

const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if(entry.isIntersecting){
            entry.target.classList.add('visible');
        }
    });
}, options);

reveals.forEach(reveal => {
    observer.observe(reveal);
});
