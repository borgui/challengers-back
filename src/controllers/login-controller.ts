import * as jwt from 'jsonwebtoken';

class LoginController {
	public static perform (req, res): any {
		req.assert('email', 'E-mail cannot be blank').notEmpty();
		req.assert('email', 'E-mail is not valid').isEmail();
		req.assert('password', 'Password cannot be blank').notEmpty();
		req.assert('password', 'Password length must be atleast 8 characters').isLength({ min: 8 });
		req.sanitize('email').normalizeEmail({ gmail_remove_dots: false });

		const errors = req.validationErrors();
		if (errors) {
			return res.json({
				errors
			});
		}

		const _email = req.body.email.toLowerCase();
		const _password = req.body.password;
	}
}

export default LoginController;
