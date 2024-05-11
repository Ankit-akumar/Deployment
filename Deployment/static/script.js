const loadButton = 
	document.getElementById('loadButton'); 
const loader = 
	document.getElementById('loader'); 
const demoForm = 
	document.getElementById('my-form'); 

loadButton.addEventListener('click', () => { 
	loadButton.disabled = true; 
	loader.style.display = 'inline-block'; 

	setTimeout(() => { 
		loadButton.disabled = false; 
		loader.style.display = 'none'; 
		demoForm.reset(); 
	}, 2000); 
});
