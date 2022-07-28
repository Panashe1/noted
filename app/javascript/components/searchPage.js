
const artistList = document.querySelector(".search--artist");
const albumList = document.querySelector(".search--albums");
const trackList = document.querySelector(".search--tracks");

const artistBtn = document.querySelector("#radio1");
const albumsBtn = document.querySelector("#radio2");
const tracksBtn = document.querySelector("#radio3");


function toggleSearchFilter() {
  initializeFilter();
  createFilterBtnEL();
};

const createFilterBtnEL = () => {
  artistBtn.addEventListener('click', (e) => {
    artistList.style = "display: grid";
    albumList.style = "display: none";
    trackList.style = "display: none";
  });

  albumsBtn.addEventListener('click', (e) => {
    albumList.style = "display: grid";
    artistList.style = "display: none";
    trackList.style = "display: none";
  });

  tracksBtn.addEventListener('click', (e) => {
    trackList.style = "display: grid";
    artistList.style = "display: none";
    albumList.style = "display: none";
  });
};

const initializeFilter = () => {
  albumList.style = "display: none";
  trackList.style = "display: none";
}

export default toggleSearchFilter;
