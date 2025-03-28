/**
 * Creaking sound effect for the mode dial
 * 
 * This file contains a base64-encoded WAV sound effect of a creaking noise
 * for use with the mode switcher dial.
 * 
 * In a full implementation, you would use a real audio file instead.
 * This is a placeholder that contains a simple sound wave to demonstrate
 * the concept.
 */

const dialCreakSound = `data:audio/wav;base64,UklGRigAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQQAAAAAAA==`;

/**
 * Play the creaking sound effect
 */
function playCreakSound() {
    try {
        const audio = new Audio(dialCreakSound);
        audio.play();
    } catch (e) {
        console.log("Unable to play sound effect:", e);
    }
}

// If running in a browser environment, expose the function globally
if (typeof window !== 'undefined') {
    window.playCreakSound = playCreakSound;
}