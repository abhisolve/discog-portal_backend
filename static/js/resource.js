const cookie = getCookie('csrftoken');

let initialPageUrl = '/api/v1/student-portal/assigned-resources-for-student/?page=1'

let hasbeenemptied = false;

const urlsHit = [];

$(window).scroll(function() {
    //if($(window).scrollTop() + window.innerHeight == $(document).height()) {
    if($(document).height() - window.innerHeight == $(document).scrollTop() && $(document).scrollTop() != 0) {
	if (initialPageUrl != null){
            $("#loader").attr("hidden", false);
            populateCards();
        }
    }
})


let renderedResources = [];

const populateCards = () => {
   
    if (hasbeenemptied != true){
        $(".row").empty();
        hasbeenemptied = true;
    }
    
    if (urlsHit.indexOf(initialPageUrl) < 0 && initialPageUrl != null){
        $.ajax({
            url: `${initialPageUrl}`,
            type: 'get',
            headers: {'X-CSRFToken': cookie},
            success: (res) => {
                $("#loader").attr("hidden", true);
                for (let result of res.results){
                    if (renderedResources.indexOf(result.id) < 0){
                        $(".row").append(
                            `
<div class="col-sm-4">
                            <div class="card">
                                <div class="card-header text-center">
                                    <h4 class="card-title mb-0"><a  href="view-resource/${result.id}">${result.resource_title}</a></h4>
                                </div>
                                <a href="view-resource/${result.id}">
                                    <img src="${result.resource_cover_image}" alt="${result.resource_title}" class="img-thumbnail" style="width:296px; height:160px;">
                                </a>
                                <div class="card-body">
                                    ${result.resource_description}
                                </div>
                            </div>
</div>
                        `
                        )
                    renderedResources.push(result.id);
                    }
                }
                urlsHit.push(initialPageUrl);

                if (res.next !== 'null'){
                    initialPageUrl = res.next
                }else{
                    console.log("error")
                }
            },
            error: (res) => {
                console.log("error");
            }
        });
    }
}
