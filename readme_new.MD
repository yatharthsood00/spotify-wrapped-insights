# Spotify Wrapped Insights - Evolution

This is a branch created to start work on a backend that can be then used to generate a Web page that can show the highlights of the insights generated at a glance, all the way from pulling the playlist data, to generating all the smaller/larger insights, and the option to create playlists off of the data that was categorised and created.

## TODO (approximate):
1. Move all the Jupyter Notebooks content to a Py script that is executed once (and asynchronously), and outputs the necessary data needed for the Web page as JSONs, etc.
2. Also have the same script also get the playlist information first of all, so that it is all done in one go, with proper error logging and catching.
3. Make minimal use of frameworks for the frontend, but make sure that it is dynamic enough that it can take user input and then call the script as required.
4. Keep adding more insights, to the Notebook, that still gets updated in the ```master``` branch.
