const tg = window.Telegram.WebApp;

tg.ready();
tg.expand();

console.log("Neyronrobot Mini App ishga tushdi!");

function showMessage(message) {
    tg.showAlert(message);
}