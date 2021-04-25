console.log('Scripts loaded!')
try {
	carouselsArr
} catch(e) {
	carouselsArr = []
}

if (carouselsArr.length > 0) {
	$(document).ready(function() {
		for (let carouselId of carouselsArr) {
			$(carouselId).owlCarousel({
				loop: false,
				margin: 13,
				nav: false,
				dot: false,
				responsive: {
					1200: {
						items: 4,
					}
				}
			})
		}
	})
}
