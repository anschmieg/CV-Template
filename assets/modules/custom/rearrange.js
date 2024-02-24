import $ from 'jquery';

function rearrangePage() {
    console.log("Rearranging page...");
    $('#name').appendTo('#left-panel');
}

export { rearrangePage };
