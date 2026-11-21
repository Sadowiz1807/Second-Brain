'use strict';

function applyBackground(response) {
  if (!response.ok) {
    notice(response.error);
    return;
  }
  if (response.image) {
    $('universe').style.backgroundImage = `url("${response.image}")`;
  }
}

$('change-background').onclick = async () => {
  const control = $('change-background');
  control.disabled = true;
  try {
    const response = await window.pywebview.api.change_background();
    if (!response.cancelled) {
      applyBackground(response);
    }
  } catch (error) {
    notice(String(error));
  } finally {
    control.disabled = false;
  }
};

window.addEventListener('pywebviewready', async () => {
  // Some isolated visual-test bridges expose only catalog operations.
  if (!window.pywebview.api.get_background) {
    return;
  }
  try {
    applyBackground(await window.pywebview.api.get_background());
  } catch (error) {
    notice(String(error));
  }
});
