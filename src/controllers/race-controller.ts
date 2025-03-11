import * as jwt from 'jsonwebtoken';

class RaceController {
	public static perform (req, res): any {

		req.sanitize('email').normalizeEmail({ gmail_remove_dots: false });

		const errors = req.validationErrors();
		if (errors) {
			return res.json({
				errors
			});
		}
	}
}

export default RaceController;
